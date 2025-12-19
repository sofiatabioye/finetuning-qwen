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
    # Convert '""' values in JSON to Python's 'None'
    for field, field_data in json_data.items():
        if field_data.get('value') == '""':
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

json_output ={"PatientSurname": {"value": "Doe3", "bbox": [0.042382, 0.214559, 0.354719, 0.244661]}, "PatientForeName": {"value": "John", "bbox": [0.356291, 0.214559, 0.670133, 0.243547]}, "DateReferral": {"value": "15/02/2024", "bbox": [0.397348, 0.304833, 0.676481, 0.345024]}, "DateOfDecisionToRefer": {"value": "15/02/2024", "bbox": [0.39892, 0.274727, 0.681197, 0.302649]}, "GPPracticeName": {"value": "GP Saint Road", "bbox": [0.392667, 0.244661, 0.674909, 0.271474]}, "GPFaxNumber": {"value": "", "bbox": [0.400493, 0.27365, 0.676481, 0.287038]}, "GPPracticeEmail": {"value": "", "bbox": [0.401065, 0.284835, 0.674909, 0.301648]}, "HospitalNumber": {"value": "G111113", "bbox": [0.039238, 0.302702, 0.395707, 0.340673]}, "LandlineNumber": {"value": "", "bbox": [0.043954, 0.341737, 0.395707, 0.363966]}, "MobileNumber": {"value": "", "bbox": [0.042382, 0.362949, 0.395707, 0.380817]}, "ConsentToText": {"value": "Yes", "bbox": [0.039238, 0.382995, 0.427825, 0.401983]}, "InterpreterRequired": {"value": "No", "bbox": [0.04081, 0.370693, 0.427825, 0.393054]}, "CapacityToConsent": {"value": "Yes", "bbox": [0.043954, 0.400805, 0.437667, 0.417563]}, "GPDeclaration": {"value": "They have symptoms which may be caused by cancer\nI have informed the patient:\nThat they are being referred to the rapid access suspected cancer clinic\nThe nature of the tests likely to take place\nI have provided the patient with a 2 week wait information leaflet", "bbox": [0.036094, 0.42197, 0.676481, 0.537861]}, "AbdominalMass": {"value": "No", "bbox": [0.05659, 0.560542, 0.670133, 0.580644]}, "UnexplainedRectalMass": {"value": "No", "bbox": [0.05659, 0.583971, 0.668953, 0.603022]}, "AnalUlceration": {"value": "No", "bbox": [0.058162, 0.604073, 0.667277, 0.623061]}, "RectalBleeding": {"value": "No", "bbox": [0.064444, 0.650931, 0.665917, 0.684456]}, "ChangeInBowelHabit": {"value": "No", "bbox": [0.0613, 0.682199, 0.665917, 0.721234]}, "UnexplainedWeightLoss": {"value": "No", "bbox": [0.0613, 0.721234, 0.665917, 0.77254]}, "IronDeficiencyAnaemia": {"value": "No", "bbox": [0.058162, 0.77254, 0.664509, 0.813846]}}# Call the function to visualize the image
visualize_bboxes_on_image('images/2WW form for suspected colon cancer April 2023 3_page_1.png', json_output, output_path='visualized_image.png')
