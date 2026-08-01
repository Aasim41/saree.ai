import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from inference.generate import generate_variant_image


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
    os.makedirs(output_dir, exist_ok=True)

    prompt = (
        "A highly detailed, intricate Banarasi silk saree design, rich gold zari work, "
        "deep terracotta red background, floral motifs, traditional Indian textile, "
        "highly detailed, seamless pattern."
    )

    image = generate_variant_image(prompt=prompt)
    if image is None:
        print("ERROR: Generation failed. Ensure LoRA exists at training/output/saree_lora.safetensors")
        sys.exit(1)

    output_path = os.path.join(output_dir, "lora_test_generation.png")
    image.save(output_path)
    print(f"Success! Image saved to {output_path}")


if __name__ == "__main__":
    main()
