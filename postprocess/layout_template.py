import argparse
import os
import json
import zipfile
from PIL import Image, ImageCms

def convert_to_cmyk(img):
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    icc_path = "USWebCoatedSWOP.icc"
    if os.path.exists(icc_path):
        try:
            srgb_profile = ImageCms.createProfile("sRGB")
            cmyk_profile = ImageCms.getOpenProfile(icc_path)
            return ImageCms.profileToProfile(img, srgb_profile, cmyk_profile, outputMode='CMYK')
        except:
            pass
    return img.convert('CMYK')

def build_saree_layout(body_tile_path, border_path, pallu_path, output_path, print_ready=False, scale=0.1, fabric="Silk", width=115):
    dpi = 300
    
    if not print_ready:
        return
        
    print("Generating TexFlow Manufacturer Export Package (ZIP)...")
    os.makedirs("temp_export", exist_ok=True)
    
    body = Image.open(body_tile_path)
    body_cmyk = convert_to_cmyk(body)
    body_cmyk.save("temp_export/body_cmyk.tiff", format="TIFF", dpi=(dpi,dpi))
    
    layout_spec = {
        "production_requirements": {
            "fabric_type": fabric,
            "target_print_width_cm": int(width),
            "target_dpi": dpi,
            "color_space": "CMYK",
            "icc_profile": "USWebCoatedSWOP"
        },
        "instructions": {
            "body": "Repeat seamlessly across remaining canvas area."
        }
    }
    
    with open("temp_export/layout_spec.json", "w") as f:
        json.dump(layout_spec, f, indent=4)
        
    zip_path = output_path if output_path.endswith('.zip') else output_path + '.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write("temp_export/body_cmyk.tiff", "body_cmyk.tiff")
        zipf.write("temp_export/layout_spec.json", "machine_instructions.json")
        
    print(f"Package saved to {zip_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--body", required=True)
    parser.add_argument("--border", required=True)
    parser.add_argument("--pallu", required=True)
    parser.add_argument("--out", default="layout_output.jpg")
    parser.add_argument("--print-ready", action="store_true")
    parser.add_argument("--scale", type=float, default=0.1)
    parser.add_argument("--fabric", default="Silk")
    parser.add_argument("--width", default="115")
    args = parser.parse_args()
    
    build_saree_layout(args.body, args.border, args.pallu, args.out, print_ready=args.print_ready, scale=args.scale, fabric=args.fabric, width=args.width)
