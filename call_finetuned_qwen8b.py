import json
import os
import sys
import time
from pathlib import Path
from unsloth import FastVisionModel
from PIL import Image
import torch

# Configuration
MODEL_REPO = "sophy/qwen3-vl-4b-referral-forms"
USER_MESSAGES_PATH = "schemas/user_messages_test.jsonl"
OUTPUT_DIR = "llm_outputs/finetuned_qwen4b/results"
BASE_IMAGE_DIR = "."  # Base directory for images (adjust if needed)

# Parse command-line arguments
target_line_number = None
if len(sys.argv) > 1:
    try:
        target_line_number = int(sys.argv[1])
        print(f"Target line number: {target_line_number}")
    except ValueError:
        print(f"Warning: Invalid line number '{sys.argv[1]}', processing all items")

# Check GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")
    gpu_props = torch.cuda.get_device_properties(0)
    print(f"GPU Memory: {gpu_props.total_memory / 1024**3:.2f} GB")
    print(f"CUDA Cores: {gpu_props.multi_processor_count}")
    # Enable GPU optimizations
    torch.backends.cudnn.benchmark = True  # Optimize for consistent input sizes
    torch.backends.cuda.matmul.allow_tf32 = True  # Enable TF32 for faster matmul (Ampere+)
    print("✅ GPU optimizations enabled")
else:
    print("⚠️  WARNING: No GPU detected! Processing will be slow on CPU.")

# Load model once at startup
# With 48GB VRAM (A6000), we can use 8-bit for faster inference than 4-bit
# If you want even faster, you could use load_in_4bit=False (full precision)
# but that would use more memory (~16GB for 4B model)
print(f"\nLoading model {MODEL_REPO}...")
try:
    # Try 8-bit first (faster than 4-bit, uses ~8GB VRAM for 4B model)
    from transformers import BitsAndBytesConfig
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
    )
    model, tokenizer = FastVisionModel.from_pretrained(
        MODEL_REPO,
        quantization_config=quantization_config,
        device_map="auto",
    )
    print("✅ Loaded in 8-bit (faster than 4-bit)")
except Exception as e:
    print(f"⚠️  8-bit loading failed: {e}")
    print("Falling back to 4-bit...")
    model, tokenizer = FastVisionModel.from_pretrained(
        MODEL_REPO,
        load_in_4bit=True,
        device_map="auto",
    )
FastVisionModel.for_inference(model)

# Verify model is on GPU
model_device = next(model.parameters()).device
print(f"Model device: {model_device}")
if str(model_device).startswith("cuda"):
    print("✅ Model is on GPU!")
    # Try to compile model for faster inference (PyTorch 2.0+)
    try:
        if hasattr(torch, 'compile'):
            print("Compiling model for faster inference...")
            model = torch.compile(model, mode="reduce-overhead")
            print("✅ Model compiled successfully!")
        else:
            print("ℹ️  torch.compile not available (requires PyTorch 2.0+)")
    except Exception as e:
        print(f"⚠️  Could not compile model: {e} (continuing without compilation)")
else:
    print("⚠️  WARNING: Model is not on GPU!")

print("Model loaded successfully!")

# Create output directory
output_path = Path(OUTPUT_DIR)
output_path.mkdir(parents=True, exist_ok=True)
print(f"Output directory: {output_path}")

# Process each item in the JSONL file
print(f"\nProcessing items from {USER_MESSAGES_PATH}...")
with open(USER_MESSAGES_PATH, 'r', encoding='utf-8') as f:
    total_items = 0
    processed_items = 0
    
    for line_num, line in enumerate(f, 1):
        if not line.strip():
            continue
        
        try:
            # Parse JSON line
            item = json.loads(line)
            item_index = item.get('item_index', line_num)
            
            # Skip if we're targeting a specific line number and this isn't it
            # (line_num is 1-indexed, matching the line number in the file)
            if target_line_number is not None and line_num != target_line_number:
                continue
            
            user_message = item.get('user_message', {})
            
            # Extract image path from user_message content
            image_path = None
            content = user_message.get('content', [])
            
            for content_item in content:
                if content_item.get('type') == 'image':
                    image_path = content_item.get('image')
                    break
            
            if not image_path:
                print(f"  [{line_num}] Item {item_index}: No image found, skipping")
                continue
            
            # Construct full image path
            full_image_path = Path(BASE_IMAGE_DIR) / image_path
            if not full_image_path.exists():
                print(f"  [{line_num}] Item {item_index}: Image not found: {full_image_path}, skipping")
                continue
            
            total_items += 1
            print(f"  [{line_num}] Item {item_index}: Processing {image_path}...")
            
            # Start timing
            start_time = time.time()
            
            # Load image
            image = Image.open(full_image_path).convert("RGB")
            
            # Use the user_message directly (it already has the correct structure)
            messages = [user_message]
            
            # Generate prompt
            prompt = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=False,
            )
            
            # Tokenize
            inputs = tokenizer(image, prompt, return_tensors="pt")
            # Ensure all inputs are on the same device as the model
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Generate with optimizations for speed
            # Use torch.inference_mode() for better performance than no_grad()
            with torch.inference_mode():
                out = model.generate(
                    **inputs,
                    max_new_tokens=3000,  # Reduced from 5000 for faster generation (adjust if needed)
                    temperature=0.1,  # Lower temperature = faster, more deterministic
                    top_p=0.8,  # Lower top_p = faster sampling
                    do_sample=True,  # Keep sampling for quality
                    pad_token_id=tokenizer.eos_token_id,  # Avoid padding warnings
                    use_cache=True,  # Enable KV cache for faster generation
                    num_beams=1,  # Greedy decoding (faster than beam search)
                )
            
            # Decode output
            result_text = tokenizer.decode(out[0], skip_special_tokens=True)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Extract filename (without extension) for output folder
            image_filename = Path(image_path).stem
            
            # Save result to JSON file
            output_filename = f"{image_filename}_finetuned_qwen4b.json"
            output_file = output_path / output_filename
            
            # Parse the result to extract JSON (if it's wrapped in text)
            # Try to extract JSON from the result
            try:
                # The result might be just JSON or JSON wrapped in text
                # Try to find JSON object in the result
                result_json = json.loads(result_text)
            except json.JSONDecodeError:
                # If direct parsing fails, try to extract JSON from text
                # Look for JSON-like content
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    try:
                        result_json = json.loads(json_match.group())
                    except:
                        # If still fails, save as text
                        result_json = {"raw_output": result_text}
                else:
                    result_json = {"raw_output": result_text}
            
            # Save in the same format as other models: {"image_path": "...", "fields": {...}}
            # Extract fields from the result_json structure
            if "extraction" in result_json and "fields" in result_json["extraction"]:
                fields = result_json["extraction"]["fields"]
            elif "fields" in result_json:
                fields = result_json["fields"]
            else:
                fields = result_json
            
            output_data = {
                "image_path": image_path,
                "fields": fields,
                "processing_time_seconds": round(processing_time, 2)
            }
            
            with open(output_file, 'w', encoding='utf-8') as out_f:
                json.dump(output_data, out_f, indent=2, ensure_ascii=False)
            
            processed_items += 1
            print(f"    ✓ Saved to: {output_file} (took {processing_time:.2f}s)")
            
        except json.JSONDecodeError as e:
            print(f"  [{line_num}] Error parsing JSON: {e}")
            continue
        except Exception as e:
            print(f"  [{line_num}] Item {item_index}: Error processing: {e}")
            import traceback
            traceback.print_exc()
            continue

print(f"\n✓ Processing complete!")
if target_line_number is not None:
    if processed_items == 0:
        print(f"  ⚠ Line {target_line_number} not found or had no valid image!")
    else:
        print(f"  ✓ Processed line {target_line_number}")
else:
    print(f"  Total items processed: {processed_items}/{total_items}")
print(f"  Results saved to: {output_path}")
