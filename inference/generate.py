import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")
DEFAULT_LORA_PATH = os.path.join(ROOT_DIR, "training", "output", "saree_lora.safetensors")
BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

_pipe = None
_loaded_lora: Optional[str] = None


def _get_lora_path(lora: Optional[str]) -> str:
    if lora and os.path.isfile(lora):
        return lora
    return DEFAULT_LORA_PATH


def _load_pipeline(lora_path: str):
    global _pipe, _loaded_lora

    import torch
    from diffusers import StableDiffusionXLPipeline

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if _pipe is None:
        logger.info("Loading SDXL pipeline on %s", device)
        _pipe = StableDiffusionXLPipeline.from_pretrained(
            BASE_MODEL,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32,
            use_safetensors=True,
        ).to(device)

    if os.path.isfile(lora_path) and _loaded_lora != lora_path:
        logger.info("Loading LoRA weights from %s", lora_path)
        _pipe.load_lora_weights(lora_path)
        _loaded_lora = lora_path

    return _pipe


def generate_variant_image(
    prompt: str,
    lora: str = "",
    seed: int = 42,
    negative_prompt: str = "blurry, low quality, distorted, watermark, human, person, draped, 3d render",
):
    """
    Generate a saree design variant using SDXL + LoRA.
    Returns a PIL Image, or None if GPU/LoRA unavailable.
    """
    lora_path = _get_lora_path(lora)
    if not os.path.isfile(lora_path):
        logger.warning("LoRA not found at %s — cannot run real generation", lora_path)
        return None

    try:
        import torch
        from PIL import Image

        pipe = _load_pipeline(lora_path)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cpu":
            logger.warning("CUDA unavailable — SDXL generation will be very slow")

        generator = torch.Generator(device=device).manual_seed(seed)
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=30,
            guidance_scale=7.5,
            generator=generator,
        ).images[0]
        return result
    except Exception as exc:
        logger.exception("Generation failed: %s", exc)
        return None
