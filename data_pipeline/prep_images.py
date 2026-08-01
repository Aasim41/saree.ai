import os
import argparse
from PIL import Image

def resize_and_crop(img, target_size=(1024, 1024), crop_mode="center"):
    """Resizes and crops an image to exactly target_size without distortion."""
    target_ratio = target_size[0] / target_size[1]
    img_ratio = img.width / img.height
    
    if img_ratio > target_ratio:
        # Image is wider than target ratio
        new_height = target_size[1]
        new_width = int(new_height * img_ratio)
    else:
        # Image is taller than target ratio
        new_width = target_size[0]
        new_height = int(new_width / img_ratio)
        
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Calculate crop box based on crop_mode
    if crop_mode == "center":
        left = (img.width - target_size[0]) / 2
        top = (img.height - target_size[1]) / 2
    elif crop_mode == "top":
        left = (img.width - target_size[0]) / 2
        top = 0
    elif crop_mode == "bottom":
        left = (img.width - target_size[0]) / 2
        top = img.height - target_size[1]
    elif crop_mode == "left":
        left = 0
        top = (img.height - target_size[1]) / 2
    elif crop_mode == "right":
        left = img.width - target_size[0]
        top = (img.height - target_size[1]) / 2
    else:
        raise ValueError(f"Unknown crop_mode: {crop_mode}")
        
    right = left + target_size[0]
    bottom = top + target_size[1]
    
    return img.crop((left, top, right, bottom))

def main():
    parser = argparse.ArgumentParser(description="Resize and crop dataset images without distortion.")
    parser.add_argument("--input_dir", required=True, help="Directory with raw images")
    parser.add_argument("--output_dir", required=True, help="Directory to save processed images")
    parser.add_argument("--crop_mode", default="center", choices=["center", "top", "bottom", "left", "right"], help="Crop mode to preserve important edges like borders/pallus.")
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    count = 0
    for filename in os.listdir(args.input_dir):
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
            
        in_path = os.path.join(args.input_dir, filename)
        out_path = os.path.join(args.output_dir, filename)
        
        try:
            with Image.open(in_path) as img:
                img = img.convert("RGB")
                processed = resize_and_crop(img, (1024, 1024), crop_mode=args.crop_mode)
                processed.save(out_path, quality=95)
                count += 1
                print(f"Processed: {filename} with crop_mode={args.crop_mode}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    print(f"Successfully processed {count} images.")

if __name__ == "__main__":
    main()
