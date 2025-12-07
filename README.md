# Fine-tuning Qwen3-VL-8B for Referral Form Extraction

This repository contains code for fine-tuning Qwen3-VL-8B (a vision-language model) using Unsloth to extract structured data from referral forms. The model learns to extract field values and their bounding box coordinates from form images.

## Overview

The fine-tuning process uses:
- **Model**: Qwen3-VL-8B-Instruct (8 billion parameter vision-language model)
- **Framework**: Unsloth (for fast, memory-efficient training)
- **Quantization**: 4-bit (BNB) to reduce memory requirements
- **Method**: LoRA (Low-Rank Adaptation) - only trains a small subset of parameters

## Prerequisites

- Python 3.10+
- CUDA-capable GPU (NVIDIA GPU with at least 16GB VRAM recommended)
- CUDA Toolkit 12.x
- PyTorch 2.9+

## Installation

1. Install required packages:

```bash
pip install -U "unsloth>=2024.10.0" "transformers>=4.57.0" datasets pillow accelerate bitsandbytes trl
```

2. Verify CUDA availability:

```python
import torch
print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("CUDA device count:", torch.cuda.device_count())
    print("Current device:", torch.cuda.current_device())
    print("Device name:", torch.cuda.get_device_name(0))
```

## Dataset Format

Your training dataset should be a JSONL file where each line contains a conversation in the following format:

```json
{
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are a referral form assistant. Extract a structured JSON response following the known schema. Include both the extracted values and their bounding boxes. Leave missing fields as null."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Extract all fields from this referral form and return your answer as a JSON object."
        },
        {
          "type": "image",
          "image": "images/gp-referral-cancer-colorectal IOV108_page_1.png"
        }
      ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "{\"PatientSurname\": {\"value\": \"T108\", \"bbox\": [0.043954, 0.218127, 0.233253, 0.240445]}, ...}"
        }
      ]
    }
  ]
}
```

### Key Points:
- **Image paths**: Should be relative to the root directory where training is run
- **Bounding boxes**: Normalized format `[x_min, y_min, x_max, y_max]` where values are between 0.0 and 1.0
- **Assistant output**: Must be a JSON string containing field names, values, and bounding boxes

## Training Steps

### 1. Load Dataset

```python
from datasets import load_dataset

DATA_PATH = "training_dataset.jsonl"  # Your JSONL file
IMAGES_ROOT = "."  # Root directory for images

dataset = load_dataset(
    "json",
    data_files={"train": DATA_PATH},
)["train"]

# Convert to Python list (required by SFTTrainer for vision)
train_data = dataset.to_list()
print("Loaded examples:", len(train_data))
```

### 2. Convert Messages for Vision Format

The dataset needs to be converted to ensure image blocks are properly formatted:

```python
def convert_for_vision(example):
    new_messages = []
    
    for msg in example["messages"]:
        role = msg["role"]
        blocks = []
        
        for block in msg["content"]:
            b_type = block.get("type")
            
            if b_type == "text":
                blocks.append({
                    "type": "text",
                    "text": block["text"],
                })
            elif b_type == "image":
                blocks.append({
                    "type": "image",
                    "image": block["image"],  # string path only
                })
            else:
                blocks.append({
                    "type": "text",
                    "text": str(block),
                })
        
        new_messages.append({
            "role": role,
            "content": blocks,
        })
    
    return {"messages": new_messages}

converted_ds = [convert_for_vision(ex) for ex in train_data]
```

### 3. Load Model and Setup LoRA

```python
from unsloth import FastVisionModel, is_bf16_supported
from unsloth.trainer import UnslothVisionDataCollator
from trl import SFTTrainer, SFTConfig
import torch

# Load base model in 4-bit
model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/Qwen3-VL-8B-Instruct-unsloth-bnb-4bit",
    load_in_4bit=True,
    dtype=None,  # auto dtype
    use_gradient_checkpointing="unsloth"
)

# Add LoRA adapters
model = FastVisionModel.get_peft_model(
    model,
    finetune_vision_layers=True,
    finetune_language_layers=True,
    finetune_attention_modules=True,
    finetune_mlp_modules=True,
    r=16,
    lora_alpha=16,
    lora_dropout=0.0,
    bias="none",
    target_modules="all-linear",
    use_rslora=False,  # Qwen3-VL does NOT benefit from RSLoRA
    loftq_config=None,
)

FastVisionModel.for_training(model)
print("LoRA enabled.")
```

### 4. Setup Training Configuration

```python
# Vision-aware data collator
data_collator = UnslothVisionDataCollator(model, tokenizer)

# Training config
train_args = SFTConfig(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    max_steps=300,  # Adjust based on your dataset size
    warmup_ratio=0.03,
    logging_steps=10,
    save_steps=200,
    weight_decay=0.01,
    bf16=is_bf16_supported(),
    output_dir="qwen3-vl-8b-referral-forms",
    remove_unused_columns=False,
    max_seq_length=2048,
    dataset_text_field="",
    dataset_kwargs={"skip_prepare_dataset": True},
)
```

### 5. Train the Model

```python
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=train_args,
    train_dataset=converted_ds,  # IMPORTANT: must be a Python list
    data_collator=data_collator,
)

print("Training…")
trainer.train()
print("Training complete.")
```

## Inference

After training, you can use the model for inference:

```python
from PIL import Image
import torch

FastVisionModel.for_inference(model)

def run_inference(image_path, instruction):
    image = Image.open(image_path).convert("RGB")
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": instruction},
            ],
        }
    ]
    
    input_text = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=False,
    )
    
    inputs = tokenizer(
        image,
        input_text,
        add_special_tokens=False,
        return_tensors="pt",
    ).to(model.device)
    
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=2048,
            temperature=0.2,
            top_p=0.8,
        )
    
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    return text

# Example usage
result = run_inference(
    "test.png",
    "Extract the referral form fields and return STRICT valid JSON only."
)
print(result)
```

## Saving the Model

### Option 1: Save LoRA Adapters Only

```python
adapter_dir = "qwen3-vl-8b-referral-forms-lora"
model.save_pretrained(adapter_dir)
tokenizer.save_pretrained(adapter_dir)
print("Saved LoRA adapters to", adapter_dir)
```

### Option 2: Merge LoRA into Full Model (Recommended for Deployment)

```python
merged_dir = "qwen3-vl-8b-referral-forms-merged"
model.save_pretrained_merged(merged_dir, tokenizer)
tokenizer.save_pretrained(merged_dir)
print("Saved merged model to", merged_dir)
```

### Option 3: Push to Hugging Face Hub

```python
model.push_to_hub_merged(
    "your-username/qwen3-vl-8b-referral-forms",
    tokenizer,
    token="your_hf_token"
)
```

### Option 4: Export to GGUF Format (for llama.cpp)

```python
model.save_pretrained_gguf(
    "qwen3vl_referrals_gguf",
    tokenizer=tokenizer,
    quantization_method="q4_k_m"  # or "f16" for full precision
)
```

## Loading a Trained Model

To load a previously trained model:

```python
from unsloth import FastVisionModel

MODEL_REPO = "your-username/qwen3-vl-8b-referral-forms"

model, tokenizer = FastVisionModel.from_pretrained(
    MODEL_REPO,
    load_in_4bit=True,
)

FastVisionModel.for_inference(model)
```

## Training Tips

1. **Batch Size**: Start with `per_device_train_batch_size=1` and increase if you have more VRAM
2. **Gradient Accumulation**: Use `gradient_accumulation_steps` to simulate larger batch sizes
3. **Learning Rate**: `2e-4` is a good starting point, but adjust based on your loss curve
4. **Max Steps**: Calculate based on your dataset size. For ~200 examples, 300 steps ≈ 3 epochs
5. **Image Size**: The model uses a default image size of 512. Adjust if needed for your use case

## Memory Requirements

- **Minimum**: 16GB VRAM (with 4-bit quantization)
- **Recommended**: 24GB+ VRAM for faster training
- **Full Precision**: Would require 48GB+ VRAM (not recommended)

## Troubleshooting

### Out of Memory Errors
- Reduce `per_device_train_batch_size` to 1
- Increase `gradient_accumulation_steps`
- Ensure `load_in_4bit=True`

### Poor Results
- Check your dataset format matches the expected structure
- Verify bounding boxes are in normalized format [0.0-1.0]
- Increase training steps or adjust learning rate
- Ensure assistant responses are valid JSON strings

### Image Loading Issues
- Verify image paths are correct relative to the working directory
- Check that images exist at the specified paths
- Ensure images are in RGB format

## Visualization

Use the provided `visualize_dataset_item.py` script to visualize bounding boxes:

```bash
python visualize_dataset_item.py training_dataset.jsonl 1 --output visualized.png
```

## License

This project uses Unsloth, which is free for research and commercial use. See the [Unsloth license](http://github.com/unslothai/unsloth) for details.

## References

- [Unsloth Documentation](https://github.com/unslothai/unsloth)
- [Qwen3-VL Model Card](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct)
- [Transformers Documentation](https://huggingface.co/docs/transformers)

