import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def visualize_bboxes_on_image(image_path, json_data, output_path=None):
    """
    Visualize bounding boxes from a JSON output on the given image.
    
    Args:
        image_path: Path to the image file.
        json_data: Dictionary containing the bounding box data with field names and coordinates.
        output_path: Path to save the visualization (optional).
    
    Returns:
        PIL Image with bounding boxes drawn.
    """
    # Convert 'null' values in JSON to Python's 'None'
    for field, field_data in json_data.items():
        if field_data.get('value') == 'null':
            field_data['value'] = None

    # Load the image
    full_image_path = Path(image_path)
    if not full_image_path.exists():
        raise FileNotFoundError(f"Image not found: {full_image_path}")
    
    image = Image.open(full_image_path).convert("RGB")
    img_width, img_height = image.size
    
    # Draw bounding boxes on the image
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
    
    # Iterate through JSON data and draw bounding boxes
    for idx, (field_name, field_data) in enumerate(json_data.items()):
        if not isinstance(field_data, dict):
            continue
        
        # Extract bbox - can be in different formats
        bbox = field_data.get('bbox', [])
        
        # Handle different bbox formats
        if isinstance(bbox, list) and len(bbox) >= 4:
            val0, val1, val2, val3 = bbox[0], bbox[1], bbox[2], bbox[3]
            
            # Check if it's [x_min, y_min, x_max, y_max] or [x, y, width, height]
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
            value = "No value"
        
        # Draw label and value
        label_text = f"{field_name}"
        if value and value != "No value":
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

# Example JSON output
json_output ={
    "PatientName": {"value": "Ms Green", "type": "text", "bbox": [0.127822, 0.230459, 0.495519, 0.246058]}, "ReferringClinicianName": {"value": "Dr Good", "type": "text", "bbox": [0.514123, 0.230459, 0.903999, 0.247169]}, "NHSNumber": {"value": "01", "type": "text", "bbox": [0.127822, 0.247169, 0.495519, 0.26388]}, "ReferringClinicianAddress": {"value": "Birmingham", "type": "text", "bbox": [0.514123, 0.249392, 0.903999, 0.265036]}, "DateOfBirth": {"value": "6/1/71", "type": "text", "bbox": [0.127822, 0.26388, 0.286124, 0.277214]}, "Age": {"value": "54", "type": "text", "bbox": [0.394192, 0.26388, 0.490303, 0.279479]}, "Gender": {"value": "female", "type": "text", "bbox": [0.127822, 0.279479, 0.495519, 0.293924]}, "Address": {"value": "5 Timbuktu Street", "type": "text", "bbox": [0.127822, 0.295078, 0.495519, 0.313556]}, "Telephone": {"value": "", "type": "text", "bbox": [0.127822, 0.317299, 0.495519, 0.331744]}, "MobileNumber": {"value": "", "type": "text", "bbox": [0.127822, 0.337189, 0.495519, 0.353899]}, "Email": {"value": "", "type": "text", "bbox": [0.127822, 0.355667, 0.495519, 0.372377]}, "ConsentToText": {"value": "Yes", "type": "radio", "bbox": [0.364136, 0.380072, 0.494951, 0.401168]}, "InterpreterRequired": {"value": "No", "type": "dropdown", "bbox": [0.127822, 0.40674, 0.495519, 0.437822]}, "RegisteredGP": {"value": "", "type": "text", "bbox": [0.514123, 0.404517, 0.901551, 0.435599]}, "DateOfReferral": {"value": "", "type": "date", "bbox": [0.514123, 0.373589, 0.901551, 0.394685]}, "DecisionToReferDate": {"value": "", "type": "date", "bbox": [0.514123, 0.355111, 0.901551, 0.371821]}, "Language": {"value": "", "type": "text", "bbox": [0.132394, 0.417964, 0.490303, 0.436442]}, "InformedViaText": {"value": "true", "type": "checkbox", "bbox": [0.857093, 0.494517, 0.901551, 0.525599]}, "EmphasisedUrgency": {"value": "true", "type": "checkbox", "bbox": [0.857093, 0.527711, 0.900983, 0.553366]}, "GivenLeaflet": {"value": "true", "type": "checkbox", "bbox": [0.857093, 0.557709, 0.901551, 0.586677]}, "HospitalAwareness": {"value": "true", "type": "checkbox", "bbox": [0.857093, 0.588791, 0.900983, 0.637329]}, "DiscreteLumpOver30": {"value": "true", "type": "checkbox", "bbox": [0.122578, 0.725264, 0.900983, 0.758458]}, "DiscreteLumpUnder30": {"value": "false", "type": "checkbox", "bbox": [0.122578, 0.758458, 0.900983, 0.808116]}, "SpontaneousDischarge": {"value": "false", "type": "checkbox", "bbox": [0.122578, 0.810339, 0.900983, 0.843533]}, "NippleRetraction": {"value": "false", "type": "checkbox", "bbox": [0.122578, 0.845756, 0.900983, 0.872424]}, "SkinDistortion": {"value": "false", "type": "checkbox", "bbox": [0.122578, 0.874724, 0.900983, 0.901392]}, "UnexplainedLymphadenopathy": {"value": "false", "type": "checkbox", "bbox": [0.122578, 0.903737, 0.900983, 0.930405]}
}

# Call the function to visualize the image
visualize_bboxes_on_image('test.png', json_output, output_path='visualized_image.png')
