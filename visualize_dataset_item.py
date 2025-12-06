#!/usr/bin/env python3
"""
Function to visualize assistant output (labels and bboxes) on an image from a dataset item.
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def visualize_dataset_item(dataset_item, output_path=None):
    """
    Visualize bounding boxes from a dataset item on its image.
    
    Args:
        dataset_item: Dictionary containing a dataset entry with messages
        output_path: Path to save the visualization (optional)
    
    Returns:
        PIL Image with bounding boxes drawn
    """
    # Extract image path from user message
    image_path = None
    for msg in dataset_item.get('messages', []):
        if msg.get('role') == 'user':
            user_content = msg.get('content', [])
            if isinstance(user_content, list):
                for item in user_content:
                    if item.get('type') == 'image':
                        image_path = item.get('image')
                        break
            if image_path:
                break
    
    if not image_path:
        raise ValueError("No image path found in dataset item")
    
    # Use image path directly from JSONL
    full_image_path = Path(image_path)
    
    if not full_image_path.exists():
        raise FileNotFoundError(f"Image not found: {full_image_path}")
    
    # Load image
    image = Image.open(full_image_path).convert("RGB")
    img_width, img_height = image.size
    
    # Extract JSON from assistant message
    json_str = None
    for msg in dataset_item.get('messages', []):
        if msg.get('role') == 'assistant':
            assistant_content = msg.get('content', [])
            if isinstance(assistant_content, list):
                for item in assistant_content:
                    if item.get('type') == 'text':
                        json_str = item.get('text', '')
                        break
            elif isinstance(assistant_content, str):
                json_str = assistant_content
            if json_str:
                break
    
    if not json_str:
        raise ValueError("No assistant content found in dataset item")
    
    # Parse JSON string
    try:
        # Extract JSON from text if needed
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}')
        if start_idx != -1 and end_idx != -1:
            json_str = json_str[start_idx:end_idx + 1]
        
        json_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse JSON from assistant content: {e}")
    
    # Draw bounding boxes
    draw = ImageDraw.Draw(image)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Colors for different fields
    colors = [
        (255, 0, 0),      # Red
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (255, 255, 0),    # Yellow
        (255, 0, 255),    # Magenta
        (0, 255, 255),    # Cyan
        (255, 165, 0),    # Orange
        (128, 0, 128),    # Purple
        (255, 192, 203),  # Pink
        (0, 128, 0),      # Dark Green
    ]
    
    bbox_count = 0
    
    # Iterate through JSON data
    for idx, (field_name, field_data) in enumerate(json_data.items()):
        if not isinstance(field_data, dict):
            continue
        
        # Extract bbox - can be in different formats
        bbox = field_data.get('bbox', [])
        
        # Handle different bbox formats
        if isinstance(bbox, list) and len(bbox) >= 4:
            val0, val1, val2, val3 = bbox[0], bbox[1], bbox[2], bbox[3]
            
            # Check if it's [x_min, y_min, x_max, y_max] or [x, y, width, height]
            # In clean_dataset.jsonl, format is [x_min_norm, y_min_norm, x_max_norm, y_max_norm]
            # Detection: if val2 > val0 AND val3 > val1 AND all values are <= 1.0 (normalized)
            # then it's likely [x_min, y_min, x_max, y_max] format
            is_normalized = all(v <= 1.0 for v in [val0, val1, val2, val3])
            is_min_max_format = val2 > val0 and val3 > val1
            
            if is_normalized and is_min_max_format:
                # Format: [x_min_norm, y_min_norm, x_max_norm, y_max_norm]
                x = val0 * img_width
                y = val1 * img_height
                width = (val2 - val0) * img_width
                height = (val3 - val1) * img_height
            else:
                # Format: [x_norm, y_norm, width_norm, height_norm] or absolute
                if is_normalized:
                    # Normalized width/height
                    x = val0 * img_width
                    y = val1 * img_height
                    width = val2 * img_width
                    height = val3 * img_height
                else:
                    # Absolute coordinates
                    x = val0
                    y = val1
                    width = val2
                    height = val3
        elif isinstance(bbox, dict):
            # Absolute format: {"x": ..., "y": ..., "width": ..., "height": ...}
            x = bbox.get('x', 0)
            y = bbox.get('y', 0)
            width = bbox.get('width', 0)
            height = bbox.get('height', 0)
        else:
            continue
        
        if width <= 0 or height <= 0:
            continue
        
        # Calculate rectangle coordinates
        left = x
        top = y
        right = x + width
        bottom = y + height
        
        # Get color for this field
        color = colors[idx % len(colors)]
        
        # Draw bounding box
        draw.rectangle([left, top, right, bottom], outline=color, width=3)
        
        # Get value
        value = field_data.get('value')
        if value is None:
            value = "null"
        elif isinstance(value, (dict, list)):
            value = str(value)
        
        # Draw label and value
        label_text = f"{field_name}"
        if value and value != "null":
            label_text += f": {value}"
        
        # Calculate text position (above the box)
        text_y = max(0, top - 20)
        
        # Draw text background for better visibility
        if font:
            bbox_text = draw.textbbox((left, text_y), label_text, font=font)
        else:
            bbox_text = draw.textbbox((left, text_y), label_text)
        
        text_bg = [
            bbox_text[0] - 2,
            bbox_text[1] - 2,
            bbox_text[2] + 2,
            bbox_text[3] + 2
        ]
        draw.rectangle(text_bg, fill=(255, 255, 255, 200))
        
        # Draw text
        draw.text((left, text_y), label_text, fill=color, font=font)
        
        bbox_count += 1
    
    print(f"Drew {bbox_count} bounding boxes on image")
    
    # Determine output path
    if output_path is None:
        output_path = full_image_path.parent / f"{full_image_path.stem}_visualized{full_image_path.suffix}"
    else:
        output_path = Path(output_path)
    
    # Save visualization
    image.save(output_path)
    print(f"Saved visualization to: {output_path}")
    
    return image

def visualize_from_jsonl_line(jsonl_file, line_number, output_path=None):
    """
    Visualize a specific line from a JSONL file.
    
    Args:
        jsonl_file: Path to JSONL file
        line_number: Line number (1-indexed) to visualize
        output_path: Path to save the visualization (optional)
    
    Returns:
        PIL Image with bounding boxes drawn
    """
    jsonl_path = Path(jsonl_file)
    if not jsonl_path.exists():
        raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")
    
    # Read the specific line
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if i == line_number:
                dataset_item = json.loads(line.strip())
                return visualize_dataset_item(dataset_item, output_path)
    
    raise ValueError(f"Line {line_number} not found in {jsonl_file}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize bounding boxes from a dataset item')
    parser.add_argument('jsonl_file', help='Path to JSONL file')
    parser.add_argument('line_number', type=int, help='Line number to visualize (1-indexed)')
    parser.add_argument('--output', '-o', help='Output path for visualization (optional)', default=None)
    
    args = parser.parse_args()
    
    visualize_from_jsonl_line(
        args.jsonl_file,
        args.line_number,
        output_path=args.output
    )

