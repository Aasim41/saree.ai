import argparse
from PIL import Image, ImageChops
import numpy as np

def check_seamless(image_path, output_path, tolerance=10.0):
    """
    Checks how seamless a tile is by mathematically comparing opposing edges.
    Generates a visual offset image and returns a PASS/FAIL based on MAE (Mean Absolute Error).
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        return False

    w, h = img.size
    
    # Visual check generation
    x_offset = w // 2
    y_offset = h // 2
    offset_img = ImageChops.offset(img, x_offset, y_offset)
    offset_img.save(output_path, quality=95)
    
    # Mathematical check using numpy
    arr = np.array(img, dtype=np.float32)
    
    # Compare left edge vs right edge (horizontal seamlessness)
    left_edge = arr[:, 0, :]
    right_edge = arr[:, -1, :]
    horiz_mae = np.mean(np.abs(left_edge - right_edge))
    
    # Compare top edge vs bottom edge (vertical seamlessness)
    top_edge = arr[0, :, :]
    bottom_edge = arr[-1, :, :]
    vert_mae = np.mean(np.abs(top_edge - bottom_edge))
    
    print(f"Horizontal Edge MAE: {horiz_mae:.2f}")
    print(f"Vertical Edge MAE: {vert_mae:.2f}")
    
    if horiz_mae > tolerance or vert_mae > tolerance:
        print(f"\n[FAIL] Image {image_path} exceeds the tolerance threshold of {tolerance} and is not seamless.")
        return False
    else:
        print(f"\n[PASS] Image {image_path} is seamless within the acceptable tolerance.")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input tile image")
    parser.add_argument("--output", default="seamless_check.jpg", help="Output validation image")
    parser.add_argument("--tolerance", type=float, default=15.0, help="Max allowed Mean Absolute Error between edges")
    args = parser.parse_args()
    
    check_seamless(args.input, args.output, args.tolerance)
