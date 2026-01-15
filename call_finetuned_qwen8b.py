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

# Load model once at startup
print(f"Loading model {MODEL_REPO}...")
model, tokenizer = FastVisionModel.from_pretrained(
    MODEL_REPO,
    load_in_4bit=True,
)
FastVisionModel.for_inference(model)
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
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                out = model.generate(
                    **inputs,
                    max_new_tokens=5000,
                    temperature=1.0,
                    top_p=0.9,
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
