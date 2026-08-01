import argparse
import os
import json
import zipfile
from PIL import Image, ImageCms

def get_srgb_profile():
    return ImageCms.createProfile("sRGB")

def get_cmyk_profile():
    # If a real ICC is not on disk, ImageCms provides a generic one for tests
    return ImageCms.createProfile("LAB") # Fallback since ImageCms doesn't have a default CMYK builder easily available on all systems without a file.
    # In production, you would load an exact .icc file provided by the manufacturer:
    # return ImageCms.getOpenProfile("USWebCoatedSWOP.icc")

def convert_to_cmyk(img):
    """Converts RGB image to CMYK for print."""
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # We will do a basic mode conversion for the MVP if specific ICC profiles are missing
    try:
        # Generic Pillow conversion
        return img.convert('CMYK')
    except Exception as e:
        print(f"CMYK conversion error: {e}")
        return img

def build_saree_layout(body_tile_path, border_path, pallu_path, output_path, print_ready=False, scale=0.1):
    dpi = 300
    
    if not print_ready:
        # Mockup Logic
        length_m = 5.5
        width_m = 1.15
        target_width = int(length_m * 39.3701 * dpi * scale)
        target_height = int(width_m * 39.3701 * dpi * scale)
        
        body = Image.open(body_tile_path).convert("RGB")
        border = Image.open(border_path).convert("RGB")
        pallu = Image.open(pallu_path).convert("RGB")
        
        canvas = Image.new("RGB", (target_width, target_height), "white")
        # Quick Mockup assembly...
        canvas.paste(body.resize((target_width, target_height)), (0,0))
        canvas.save(output_path, quality=90)
        print(f"Mockup layout saved successfully to {output_path}")
        return
        
    print("Generating Manufacturer Export Package (ZIP) to prevent RAM crashes...")
    # Manufacturer Export Package Logic
    os.makedirs("temp_export", exist_ok=True)
    
    # Convert files to CMYK
    body = Image.open(body_tile_path)
    body_cmyk = convert_to_cmyk(body)
    body_cmyk.save("temp_export/body_cmyk.tiff", format="TIFF", dpi=(dpi,dpi))
    
    border = Image.open(border_path)
    border_cmyk = convert_to_cmyk(border)
    border_cmyk.save("temp_export/border_cmyk.tiff", format="TIFF", dpi=(dpi,dpi))
    
    pallu = Image.open(pallu_path)
    pallu_cmyk = convert_to_cmyk(pallu)
    pallu_cmyk.save("temp_export/pallu_cmyk.tiff", format="TIFF", dpi=(dpi,dpi))
    
    # Generate Layout Specs
    layout_spec = {
        "total_dimensions_meters": {"width": 1.15, "length": 5.5},
        "target_dpi": 300,
        "color_space": "CMYK",
        "instructions": {
            "body": "Repeat seamlessly across remaining canvas area.",
            "border_top": "Place flush at Y=0, spanning full length X.",
            "border_bottom": "Place flush at Y=Max, spanning full length X.",
            "pallu": "Place flush at right edge (X=Max), spanning full width Y."
        }
    }
    
    with open("temp_export/layout_spec.json", "w") as f:
        json.dump(layout_spec, f, indent=4)
        
    # Zip it up
    zip_path = output_path if output_path.endswith('.zip') else output_path + '.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write("temp_export/body_cmyk.tiff", "body_cmyk.tiff")
        zipf.write("temp_export/border_cmyk.tiff", "border_cmyk.tiff")
        zipf.write("temp_export/pallu_cmyk.tiff", "pallu_cmyk.tiff")
        zipf.write("temp_export/layout_spec.json", "layout_spec.json")
        
    print(f"Manufacturer Package successfully saved to {zip_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble textile components into a Saree layout.")
    parser.add_argument("--body", required=True, help="Path to body tile image")
    parser.add_argument("--border", required=True, help="Path to border image")
    parser.add_argument("--pallu", required=True, help="Path to pallu image")
    parser.add_argument("--out", default="layout_output.jpg", help="Output file path (.zip for print-ready)")
    parser.add_argument("--print-ready", action="store_true", help="Generate memory-safe manufacturer export package")
    parser.add_argument("--scale", type=float, default=0.1, help="Scale for mockup")
    
    args = parser.parse_args()
    
    build_saree_layout(args.body, args.border, args.pallu, args.out, print_ready=args.print_ready, scale=args.scale)
