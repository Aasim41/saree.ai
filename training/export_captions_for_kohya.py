"""
Export captions from SQLite to sidecar .txt files for kohya_ss / LoRA training.
Run after caption_dataset.py (or anytime captions exist in the DB).
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app", "backend"))
from sqlalchemy.orm import Session
from models import Design
from database import engine

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    exported = 0
    skipped = 0

    with Session(engine) as session:
        designs = session.query(Design).all()
        for design in designs:
            img_path = os.path.join(PROCESSED_DIR, design.filename)
            if not os.path.exists(img_path):
                skipped += 1
                continue

            caption = design.caption or ""
            if caption == "[BLIP-2 Auto-Caption Pending]":
                skipped += 1
                continue

            base, _ = os.path.splitext(design.filename)
            txt_path = os.path.join(PROCESSED_DIR, f"{base}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(caption)
            exported += 1

    print(f"Exported {exported} caption files to {PROCESSED_DIR}")
    if skipped:
        print(f"Skipped {skipped} (missing image or pending caption)")


if __name__ == "__main__":
    main()
