import os
import shutil
from ultralytics import YOLO
from PIL import Image

# ============ PARAMETERS ============
MODEL_PATH = "model.pt"
INPUT_FOLDER = r"F:\folder\subfolder"
OUTPUT_FOLDER = "crop"
CONFIDENCE_THRESHOLD = 0.5  # Prediction threshold (0.0 - 1.0)
BBOX_EXPANSION = 0.1  # Percentage to expand bbox (0.1 = 10%)
SHOW_BBOX = False  # True = show bounding box, False = hide bbox
# ====================================

# Define confidence ranges and corresponding subfolder names
CONFIDENCE_RANGES = [
    (0.95, 1.0, "0.95-1.00"),
    (0.90, 0.95, "0.90-0.95"),
    (0.85, 0.90, "0.85-0.90"),
    (0.80, 0.85, "0.80-0.85")
]

def get_confidence_folder(confidence):
    """Determine which subfolder the crop should go to based on confidence"""
    for min_conf, max_conf, folder_name in CONFIDENCE_RANGES:
        if min_conf <= confidence < max_conf:
            return folder_name
    # If confidence is not in ranges, use 'other'
    return "other"

def expand_bbox(x1, y1, x2, y2, expansion, img_width, img_height):
    """Expand the bounding box by a percentage"""
    width = x2 - x1
    height = y2 - y1
    
    # Calculate expansion in pixels
    expand_w = width * expansion
    expand_h = height * expansion
    
    # New coordinates
    new_x1 = max(0, x1 - expand_w / 2)
    new_y1 = max(0, y1 - expand_h / 2)
    new_x2 = min(img_width, x2 + expand_w / 2)
    new_y2 = min(img_height, y2 + expand_h / 2)
    
    return int(new_x1), int(new_y1), int(new_x2), int(new_y2)

def main():
    # Create main output folder
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    # Create null subfolder
    null_folder = os.path.join(OUTPUT_FOLDER, "null")
    os.makedirs(null_folder, exist_ok=True)
    
    # Create confidence range subfolders
    confidence_folders = {}
    for min_conf, max_conf, folder_name in CONFIDENCE_RANGES:
        folder_path = os.path.join(OUTPUT_FOLDER, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        confidence_folders[folder_name] = folder_path
    
    # Create 'other' folder for confidence values outside the ranges
    other_folder = os.path.join(OUTPUT_FOLDER, "other")
    os.makedirs(other_folder, exist_ok=True)
    confidence_folders["other"] = other_folder
    
    # Load YOLO model
    print(f"Loading model: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)
    
    # Supported image formats
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif')
    
    # Get all images in the input folder
    image_files = [f for f in os.listdir(INPUT_FOLDER) 
                   if f.lower().endswith(image_extensions)]
    
    print(f"Found images: {len(image_files)}")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"Bounding box expansion: {BBOX_EXPANSION * 100}%")
    print(f"Show bounding box: {SHOW_BBOX}")
    print("-" * 50)
    
    # Counters for statistics
    crop_counter = 0
    null_counter = 0
    range_counters = {folder_name: 0 for _, _, folder_name in CONFIDENCE_RANGES}
    range_counters["other"] = 0
    
    for img_file in image_files:
        img_path = os.path.join(INPUT_FOLDER, img_file)
        print(f"Processing: {img_file}")
        
        # Make prediction
        results = model.predict(img_path, conf=CONFIDENCE_THRESHOLD, verbose=False)
        
        # Open original image
        img = Image.open(img_path)
        img_width, img_height = img.size
        
        # Counter for detections in this image
        detections_in_image = 0
        
        # Process each detection
        for result in results:
            boxes = result.boxes
            
            for idx, box in enumerate(boxes):
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                
                # Expand bounding box
                x1_exp, y1_exp, x2_exp, y2_exp = expand_bbox(
                    x1, y1, x2, y2, BBOX_EXPANSION, img_width, img_height
                )
                
                # Crop image
                cropped_img = img.crop((x1_exp, y1_exp, x2_exp, y2_exp))
                
                # Optional: draw bounding box on the crop
                if SHOW_BBOX:
                    from PIL import ImageDraw
                    draw = ImageDraw.Draw(cropped_img)
                    
                    # Calculate relative position of original bbox in crop
                    rel_x1 = x1 - x1_exp
                    rel_y1 = y1 - y1_exp
                    rel_x2 = x2 - x1_exp
                    rel_y2 = y2 - y1_exp
                    
                    draw.rectangle([rel_x1, rel_y1, rel_x2, rel_y2], 
                                   outline="red", width=3)
                
                # Determine which subfolder the crop should go to
                conf_folder_name = get_confidence_folder(confidence)
                conf_folder_path = confidence_folders[conf_folder_name]
                
                # Save crop in correct subfolder
                base_name = os.path.splitext(img_file)[0]
                crop_filename = f"{base_name}_crop_{crop_counter}_conf{confidence:.2f}.jpg"
                crop_path = os.path.join(conf_folder_path, crop_filename)
                
                cropped_img.save(crop_path)
                crop_counter += 1
                detections_in_image += 1
                range_counters[conf_folder_name] += 1
                
                print(f"  └─ Crop saved in '{conf_folder_name}': {crop_filename} (conf: {confidence:.2f})")
        
        # If no detections were found, move original image to null folder
        if detections_in_image == 0:
            null_path = os.path.join(null_folder, img_file)
            shutil.copy2(img_path, null_path)
            null_counter += 1
            print(f"  └─ No detections - moved to 'null'")
    
    print("-" * 50)
    print(f"Complete!")
    print(f"  • Total crops: {crop_counter}")
    print(f"\nCrops per confidence range:")
    for _, _, folder_name in CONFIDENCE_RANGES:
        count = range_counters[folder_name]
        if count > 0:
            print(f"  • {folder_name}: {count} crops")
    if range_counters["other"] > 0:
        print(f"  • other: {range_counters['other']} crops")
    print(f"\n  • Images without detections (null): {null_counter}")

if __name__ == "__main__":
    main()
