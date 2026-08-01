import os
import sys
from PIL import Image
from sqlalchemy.orm import Session
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "app", "backend"))
from models import Design
from database import engine

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
CAPTION_PENDING = "[BLIP-2 Auto-Caption Pending]"


def write_caption_file(filename: str, caption: str) -> None:
    base, _ = os.path.splitext(filename)
    txt_path = os.path.join(PROCESSED_DIR, f"{base}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(caption)


def main():
    print("Connecting to database...")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    if device == "cpu":
        print("WARNING: Running BLIP-2 on CPU will be extremely slow.")

    print("Loading BLIP-2 model...")
    processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = Blip2ForConditionalGeneration.from_pretrained(
        "Salesforce/blip2-opt-2.7b",
        torch_dtype=dtype,
    )
    model.to(device)

    with Session(engine) as session:
        pending_designs = (
            session.query(Design)
            .filter(Design.caption == CAPTION_PENDING)
            .all()
        )

        if not pending_designs:
            print("No pending designs found. Dataset is fully captioned!")
            return

        print(f"Found {len(pending_designs)} designs to caption.")

        for idx, design in enumerate(pending_designs):
            img_path = os.path.join(PROCESSED_DIR, design.filename)
            if not os.path.exists(img_path):
                print(f"File not found: {img_path}, skipping.")
                continue

            print(f"[{idx + 1}/{len(pending_designs)}] Captioning {design.filename}...")

            try:
                image = Image.open(img_path).convert("RGB")
                prompt = "A detailed description of this textile saree design:"

                inputs = processor(image, text=prompt, return_tensors="pt")
                pixel_values = inputs["pixel_values"].to(device, dtype=dtype)
                input_ids = inputs["input_ids"].to(device)

                generated_ids = model.generate(
                    pixel_values=pixel_values,
                    input_ids=input_ids,
                    max_new_tokens=50,
                )
                generated_text = processor.batch_decode(
                    generated_ids, skip_special_tokens=True
                )[0].strip()

                final_caption = f"{generated_text}. Dominant colors: {design.dominant_colors}."
                print(f"  -> {final_caption}")

                design.caption = final_caption
                session.commit()
                write_caption_file(design.filename, final_caption)

            except Exception as e:
                print(f"Failed to caption {design.filename}: {e}")
                session.rollback()

    print("Captioning complete!")


if __name__ == "__main__":
    main()
