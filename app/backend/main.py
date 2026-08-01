from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
import uvicorn
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import database

app = FastAPI(title="Saree Design AI")

# Restricted CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    # Basic hardcoded check for MVP
    if credentials.username != "designer" or credentials.password != "saree123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.on_event("startup")
def startup():
    database.init_db()

def generate_placeholder_composite(prompt, palette, motif, border_type, pallu_type):
    canvas = Image.new("RGB", (800, 400), "white")
    draw = ImageDraw.Draw(canvas)
    
    colors = [c.strip() for c in palette.split(',')]
    main_color = colors[0] if colors else "lightgray"
    border_color = colors[1] if len(colors) > 1 else "darkgray"
    
    try: Image.new("RGB", (1,1), main_color)
    except: main_color = "lightgray"
    try: Image.new("RGB", (1,1), border_color)
    except: border_color = "darkgray"
    
    if pallu_type == "matching":
        pallu_color = main_color
    else:
        pallu_color = "gold"
        
    # Body
    draw.rectangle([0, 80, 600, 320], fill=main_color, outline="black")
    draw.text((150, 150), f"BODY TILE\nMotif: {motif}", fill="black")
    draw.text((150, 200), f"Prompt: {prompt[:50]}...", fill="black") # Dynamic prompt stamp
    
    # Borders
    if border_type != "borderless":
        draw.rectangle([0, 0, 600, 80], fill=border_color, outline="black")
        draw.text((200, 30), f"TOP BORDER: {border_type}", fill="white")
        draw.rectangle([0, 320, 600, 400], fill=border_color, outline="black")
        draw.text((200, 350), f"BOTTOM BORDER: {border_type}", fill="white")
    else:
        # Extend body if borderless
        draw.rectangle([0, 0, 600, 80], fill=main_color, outline="black")
        draw.rectangle([0, 320, 600, 400], fill=main_color, outline="black")
        draw.text((200, 30), f"NO BORDER", fill="black")
    
    # Pallu
    draw.rectangle([600, 0, 800, 400], fill=pallu_color, outline="black")
    draw.text((650, 180), f"PALLU\nStyle: {pallu_type}", fill="black")
    
    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=90)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


@app.post("/generate")
async def generate_design(
    prompt: str = Form(...),
    palette: str = Form(...),
    motif: str = Form(...),
    border: str = Form(...),
    pallu: str = Form(...),
    sketch: Optional[UploadFile] = None,
    username: str = Depends(authenticate)
):
    if sketch:
        print(f"Received sketch upload: {sketch.filename}")
        
    b64_image = generate_placeholder_composite(prompt, palette, motif, border, pallu)
    database.save_design(prompt, motif, palette, border, pallu, b64_image)
    
    return {
        "status": "success",
        "image": f"data:image/jpeg;base64,{b64_image}"
    }

@app.get("/history")
async def get_history(username: str = Depends(authenticate)):
    return {"status": "success", "history": database.get_history()}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
