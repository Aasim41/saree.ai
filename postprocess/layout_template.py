import argparse
from PIL import Image

def build_saree_layout(body_tile_path, border_path, pallu_path, output_path, print_ready=False, scale=0.1):
    """
    Assembles a Saree layout from individual components.
    A full saree is roughly 5.5m x 1.15m.
    At 300 DPI, that's ~65,000 x 13,600 pixels.
    If print_ready is True, it will attempt to generate the full resolution TIFF.
    Otherwise, it uses the provided scale (e.g. 0.1 for 10% of physical size).
    """
    # Physical dimensions in meters
    length_m = 5.5
    width_m = 1.15
    
    # 1 meter = 39.3701 inches
    # Pixels = inches * DPI
    dpi = 300
    
    if print_ready:
        target_width = int(length_m * 39.3701 * dpi)
        target_height = int(width_m * 39.3701 * dpi)
        print(f"Warning: Generating FULL PRINT SCALE layout: {target_width}x{target_height} pixels.")
        print("This may consume significant RAM and take several minutes.")
    else:
        # Scale down for mockup (e.g. 10%)
        target_width = int(length_m * 39.3701 * dpi * scale)
        target_height = int(width_m * 39.3701 * dpi * scale)
        print(f"Generating mockup layout at scale {scale}: {target_width}x{target_height} pixels.")
    
    try:
        # We increase Image max pixels to avoid DecompressionBombError for massive sizes
        Image.MAX_IMAGE_PIXELS = None 
        
        body = Image.open(body_tile_path).convert("RGB")
        border = Image.open(border_path).convert("RGB")
        pallu = Image.open(pallu_path).convert("RGB")
    except Exception as e:
        print(f"Error loading images: {e}")
        return

    # Canvas creation
    canvas = Image.new("RGB", (target_width, target_height), "white")

    # Border logic (approx 15% of width)
    border_height = int(target_height * 0.15)
    border_ratio = border.width / border.height
    border_width = int(border_height * border_ratio)
    border = border.resize((border_width, border_height), Image.Resampling.LANCZOS)
    
    # Pallu logic (approx 0.8m length, which is about 14.5% of total length)
    pallu_width = int(target_width * 0.145)
    pallu = pallu.resize((pallu_width, target_height), Image.Resampling.LANCZOS)
    
    # Body logic
    body_area_width = target_width - pallu_width
    body_area_height = target_height - (2 * border_height)
    
    # Resize body tile to maintain original aspect ratio based on a physical tile size (e.g., 0.5m x 0.5m)
    physical_tile_size_m = 0.5
    if print_ready:
        tile_px = int(physical_tile_size_m * 39.3701 * dpi)
    else:
        tile_px = int(physical_tile_size_m * 39.3701 * dpi * scale)
        
    body = body.resize((tile_px, tile_px), Image.Resampling.LANCZOS)
    
    # Assembly
    # 1. Tile the body
    for x in range(0, body_area_width, body.width):
        for y in range(border_height, target_height - border_height, body.height):
            canvas.paste(body, (x, y))
            
    # 2. Paste top and bottom borders
    for x in range(0, body_area_width, border.width):
        canvas.paste(border, (x, 0))
        canvas.paste(border, (x, target_height - border_height))
        
    # 3. Paste Pallu
    canvas.paste(pallu, (body_area_width, 0))
    
    # Save output
    if print_ready:
        # Save as TIFF with DPI info for print
        canvas.save(output_path, format='TIFF', dpi=(dpi, dpi), quality=100)
    else:
        # Save as JPG for quick preview
        canvas.save(output_path, quality=90)
        
    print(f"Layout saved successfully to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assemble textile components into a Saree layout.")
    parser.add_argument("--body", required=True, help="Path to body tile image")
    parser.add_argument("--border", required=True, help="Path to border image")
    parser.add_argument("--pallu", required=True, help="Path to pallu image")
    parser.add_argument("--out", default="layout_output.jpg", help="Output file path")
    parser.add_argument("--print-ready", action="store_true", help="Generate full physical scale 300 DPI layout")
    parser.add_argument("--scale", type=float, default=0.1, help="Scale for mockup (default 0.1). Ignored if --print-ready is used.")
    
    args = parser.parse_args()
    
    build_saree_layout(args.body, args.border, args.pallu, args.out, print_ready=args.print_ready, scale=args.scale)
