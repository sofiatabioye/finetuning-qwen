# Vision-Language Models Supported by Unsloth FastVisionModel

Based on your current setup using `FastVisionModel` from Unsloth, here are other vision-language models you can train using the **same approach**:

## Currently Supported Models

### 1. **Qwen3-VL Series** ✅ (Currently Using)
- `unsloth/Qwen3-VL-4B-Instruct-unsloth-bnb-4bit`
- `unsloth/Qwen3-VL-8B-Instruct-unsloth-bnb-4bit`
- **Status**: Fully supported with FastVisionModel
- **Use Case**: Document understanding, form extraction, OCR tasks

### 2. **LLaVA Models** ✅
- `unsloth/llava-1.5-7b-bnb-4bit`
- `unsloth/llava-1.6-vicuna-7b-bnb-4bit`
- `unsloth/llava-1.6-mistral-7b-bnb-4bit`
- **Status**: Supported via FastVisionModel
- **Use Case**: General vision-language tasks, image understanding

### 3. **Llama-3.2-Vision** ✅
- `unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit`
- `unsloth/Llama-3.2-3B-Vision-Instruct-bnb-4bit`
- **Status**: Supported with FastVisionModel
- **Use Case**: Multimodal conversations, image analysis

### 4. **Qwen2-VL Series** ✅
- `unsloth/Qwen2-VL-2B-Instruct-bnb-4bit`
- `unsloth/Qwen2-VL-7B-Instruct-bnb-4bit`
- **Status**: Supported (newer version of Qwen-VL)
- **Use Case**: Similar to Qwen3-VL, improved performance

## How to Switch Models

To train a different model, simply change the `MODEL_NAME` in your notebook:

```python
# Example: Switch to LLaVA
MODEL_NAME = "unsloth/llava-1.5-7b-bnb-4bit"

# Example: Switch to Llama-3.2-Vision
MODEL_NAME = "unsloth/Llama-3.2-11B-Vision-Instruct-bnb-4bit"

# Example: Switch to Qwen2-VL
MODEL_NAME = "unsloth/Qwen2-VL-7B-Instruct-bnb-4bit"
```

The rest of your training code remains **exactly the same**:
- Same `FastVisionModel.from_pretrained()` call
- Same `UnslothVisionDataCollator`
- Same `SFTTrainer` setup
- Same data format (messages with image/text blocks)
- 
## Model Comparison

| Model | Parameters | Best For | Memory (4-bit) |
|-------|-----------|----------|----------------|
| Qwen3-VL-4B | 4B | Document extraction, forms | ~8GB VRAM |
| Qwen3-VL-8B | 8B | Complex document tasks | ~16GB VRAM |
| LLaVA-1.5-7B | 7B | General vision tasks | ~14GB VRAM |
| Llama-3.2-11B-Vision | 11B | High-quality multimodal | ~22GB VRAM |
| Qwen2-VL-7B | 7B | Balanced performance | ~14GB VRAM |
| Qwen/Qwen2-VL-2B-Instruct | 

florence
gemma
smoL

5


qwen, llava, llama
## Important Notes

1. **Data Format**: All models use the same message format:
   ```python
   {
       "role": "user",
       "content": [
           {"type": "text", "text": "..."},
           {"type": "image", "image": "path/to/image.png"}
       ]
   }
   ```

2. **LoRA Configuration**: Most models work well with:
   - `r=16`, `lora_alpha=16`
   - `use_rslora=False` (for Qwen models)
   - `use_rslora=True` (may help for LLaVA/Llama models)

3. **Model-Specific Tips**:
   - **Qwen models**: Don't use RSLoRA (`use_rslora=False`)
   - **LLaVA models**: May benefit from RSLoRA
   - **Llama-3.2-Vision**: Check Unsloth docs for latest recommendations

## Finding More Models

To discover the latest supported models, check:
1. **Unsloth GitHub**: https://github.com/unslothai/unsloth
2. **Hugging Face**: Search for `unsloth/*vision*` or `unsloth/*vl*`
3. **Unsloth Documentation**: Look for "FastVisionModel" examples

## Quick Test

To test if a model works with your setup:

```python
from unsloth import FastVisionModel

# Try loading the model
try:
    model, tokenizer = FastVisionModel.from_pretrained(
        "unsloth/MODEL-NAME-bnb-4bit",
        load_in_4bit=True,
    )
    print("✅ Model is supported!")
except Exception as e:
    print(f"❌ Model not supported: {e}")
```

## Your Current Setup Compatibility

Your current training pipeline will work with **all** the models listed above without modification, except for:
- Model name change
- Potentially adjusting `use_rslora` parameter
- Memory requirements may vary

