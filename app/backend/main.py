from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
import io
import base64
from PIL import Image, ImageDraw

app = FastAPI(title="Saree Design AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_placeholder_composite(palette, motif, border_type, pallu_type):
    """Generates a deterministic placeholder image using Pillow to represent the assembled Saree layout."""
    canvas = Image.new("RGB", (800, 400), "white")
    draw = ImageDraw.Draw(canvas)
    
    colors = [c.strip() for c in palette.split(',')]
    main_color = colors[0] if colors else "lightgray"
    border_color = colors[1] if len(colors) > 1 else "darkgray"
    
    # We use basic color names, if PIL doesn't recognize them it might throw an error.
    # So we'll use a fallback try-except.
    try:
        Image.new("RGB", (1,1), main_color)
    except:
        main_color = "lightgray"
        
    try:
        Image.new("RGB", (1,1), border_color)
    except:
        border_color = "darkgray"
    
    # Body
    draw.rectangle([0, 80, 600, 320], fill=main_color, outline="black")
    draw.text((200, 200), f"BODY TILE\nMotif: {motif}", fill="black")
    
    # Top Border
    draw.rectangle([0, 0, 600, 80], fill=border_color, outline="black")
    draw.text((200, 30), f"TOP BORDER: {border_type}", fill="white")
    
    # Bottom Border
    draw.rectangle([0, 320, 600, 400], fill=border_color, outline="black")
    draw.text((200, 350), f"BOTTOM BORDER: {border_type}", fill="white")
    
    # Pallu
    draw.rectangle([600, 0, 800, 400], fill="gold", outline="black")
    draw.text((650, 180), f"PALLU\nStyle: {pallu_type}", fill="black")
    
    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Saree Design AI Backend MVP"}

@app.post("/generate")
async def generate_design(
    prompt: str = Form(...),
    palette: str = Form(...),
    motif: str = Form(...),
    border: str = Form(...),
    pallu: str = Form(...),
    sketch: Optional[UploadFile] = None
):
    """
    MVP Endpoint.
    Currently generates a deterministic composite mockup placeholder.
    In production, this will load the correct LoRA weights and run the Diffusers pipeline.
    """
    b64_image = generate_placeholder_composite(palette, motif, border, pallu)
    
    return {
        "status": "success",
        "message": f"Generated layout mockup for {motif} motif in {palette} palette.",
        "image": f"data:image/jpeg;base64,{b64_image}"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
