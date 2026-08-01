import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "data_pipeline"))
from prep_images import resize_and_crop

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app", "backend"))

from PIL import Image
from colorthief import ColorThief
from sqlalchemy.orm import Session
from models import Design
from database import engine

src = os.path.join(os.path.dirname(__file__), "..", "data", "raw_images")
dst = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(dst, exist_ok=True)
os.makedirs(src, exist_ok=True)

print(f"Starting dataset preparation from {src}")

with Session(engine) as session:
    for fname in os.listdir(src):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        existing = session.query(Design).filter(Design.filename == fname).first()
        if existing:
            print(f"Skipping {fname} — already in database")
            continue

        path = os.path.join(src, fname)
        print(f"Processing {fname}...")

        try:
            img = Image.open(path).convert("RGB")
            img = resize_and_crop(img, (1024, 1024), crop_mode="center")
            img.save(os.path.join(dst, fname))

            color_thief = ColorThief(path)
            palette = color_thief.get_palette(color_count=3)
            hex_colors = [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in palette]
            colors_str = ", ".join(hex_colors)

            design = Design(
                filename=fname,
                dominant_colors=colors_str,
                caption="[BLIP-2 Auto-Caption Pending]",
            )
            session.add(design)
        except Exception as e:
            print(f"Error processing {fname}: {e}")

    session.commit()

print("Dataset processed and DB populated successfully.")
