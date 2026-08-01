import argparse
import os
import json
import zipfile
import shutil
import tempfile
from PIL import Image, ImageCms


def convert_to_cmyk(img):
    if img.mode != "RGB":
        img = img.convert("RGB")

    icc_path = os.path.join(os.path.dirname(__file__), "USWebCoatedSWOP.icc")
    if os.path.exists(icc_path):
        try:
            srgb_profile = ImageCms.createProfile("sRGB")
            cmyk_profile = ImageCms.getOpenProfile(icc_path)
            return ImageCms.profileToProfile(
                img, srgb_profile, cmyk_profile, outputMode="CMYK"
            )
        except Exception:
            pass
    return img.convert("CMYK")


def _save_cmyk_tiff(source_path, dest_path, dpi=300):
    img = Image.open(source_path)
    cmyk = convert_to_cmyk(img)
    cmyk.save(dest_path, format="TIFF", dpi=(dpi, dpi))


def build_saree_layout(
    body_tile_path,
    border_path,
    pallu_path,
    output_path,
    print_ready=False,
    scale=0.1,
    fabric="Silk",
    width=115,
):
    dpi = 300

    if not print_ready:
        return

    print("Generating TexFlow Manufacturer Export Package (ZIP)...")
    temp_dir = tempfile.mkdtemp(prefix="texflow_export_")
    try:
        _save_cmyk_tiff(body_tile_path, os.path.join(temp_dir, "body_cmyk.tiff"), dpi)
        _save_cmyk_tiff(border_path, os.path.join(temp_dir, "border_cmyk.tiff"), dpi)
        _save_cmyk_tiff(pallu_path, os.path.join(temp_dir, "pallu_cmyk.tiff"), dpi)

        layout_spec = {
            "production_requirements": {
                "fabric_type": fabric,
                "target_print_width_cm": int(width),
                "target_dpi": dpi,
                "color_space": "CMYK",
                "icc_profile": "USWebCoatedSWOP",
            },
            "instructions": {
                "body": "Repeat seamlessly across remaining canvas area.",
                "border": "Apply along saree edges per machine template.",
                "pallu": "Place at pallu end per layout spec.",
            },
        }

        with open(os.path.join(temp_dir, "layout_spec.json"), "w") as f:
            json.dump(layout_spec, f, indent=4)

        zip_path = output_path if output_path.endswith(".zip") else output_path + ".zip"
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(os.path.join(temp_dir, "body_cmyk.tiff"), "body_cmyk.tiff")
            zipf.write(os.path.join(temp_dir, "border_cmyk.tiff"), "border_cmyk.tiff")
            zipf.write(os.path.join(temp_dir, "pallu_cmyk.tiff"), "pallu_cmyk.tiff")
            zipf.write(os.path.join(temp_dir, "layout_spec.json"), "machine_instructions.json")

        print(f"Package saved to {zip_path}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


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

    build_saree_layout(
        args.body,
        args.border,
        args.pallu,
        args.out,
        print_ready=args.print_ready,
        scale=args.scale,
        fabric=args.fabric,
        width=args.width,
    )
