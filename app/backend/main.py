from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException, status, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uvicorn
import os
import uuid
import subprocess
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from colorthief import ColorThief

from database import get_db
import models
import schemas

current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "..", "..", ".env")
load_dotenv(env_path)

app = FastAPI(title="TexFlow Workspace")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:3000", "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

security = HTTPBasic()
AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASS = os.getenv("AUTH_PASS", "admin")

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=PROCESSED_DIR), name="images")

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != AUTH_USER or credentials.password != AUTH_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def extract_dominant_colors(image_path):
    """Use ColorThief to extract the top 3 dominant colors as hex codes."""
    try:
        color_thief = ColorThief(image_path)
        # get dominant color + palette
        palette = color_thief.get_palette(color_count=3)
        hex_colors = [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in palette]
        return ", ".join(hex_colors)
    except Exception as e:
        print(f"Color extraction failed: {e}")
        return "#ffffff, #000000"

@app.post("/upload", response_model=schemas.AssetResponse)
async def upload_asset(
    name: str = Form(...),
    collection: str = Form(...),
    fabric_type: str = Form(...),
    print_width_cm: int = Form(...),
    repeat_size_cm: int = Form(...),
    file: UploadFile = File(...),
    username: str = Depends(authenticate),
    db: Session = Depends(get_db)
):
    asset_uuid = str(uuid.uuid4())
    filename = f"{asset_uuid}_{file.filename}"
    filepath = os.path.join(PROCESSED_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())
        
    palette = extract_dominant_colors(filepath)
    
    db_asset = models.Asset(
        name=name, 
        collection=collection, 
        fabric_type=fabric_type,
        print_width_cm=print_width_cm, 
        repeat_size_cm=repeat_size_cm,
        palette=palette, 
        parent_id=None, 
        image_path=filename
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    
    return db_asset


@app.post("/generate-variant/{parent_id}", response_model=schemas.AssetResponse)
async def generate_variant(
    parent_id: int,
    new_palette: str = Form(...),
    new_repeat_cm: int = Form(...),
    username: str = Depends(authenticate),
    db: Session = Depends(get_db)
):
    parent = db.query(models.Asset).filter(models.Asset.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent asset not found")
        
    # Simulate AI variant generation using Pillow for the MVP
    img_path = os.path.join(PROCESSED_DIR, parent.image_path)
    base_img = Image.open(img_path).convert("RGB")
    
    # Just draw a simple overlay to represent a "variant"
    draw = ImageDraw.Draw(base_img)
    draw.rectangle([0, 0, 200, 50], fill="black")
    draw.text((10, 10), f"VARIANT (Scale: {new_repeat_cm}cm)", fill="white")
    
    variant_uuid = str(uuid.uuid4())
    filename = f"variant_{variant_uuid}.jpg"
    filepath = os.path.join(PROCESSED_DIR, filename)
    base_img.save(filepath, format="JPEG", quality=90)
    
    variant_asset = models.Asset(
        name=f"{parent.name} (Variant)", 
        collection=parent.collection, 
        fabric_type=parent.fabric_type,
        print_width_cm=parent.print_width_cm, 
        repeat_size_cm=new_repeat_cm,
        palette=new_palette, 
        parent_id=parent_id, 
        image_path=filename
    )
    
    db.add(variant_asset)
    db.commit()
    db.refresh(variant_asset)
    
    return variant_asset

@app.get("/assets", response_model=dict)
async def get_assets(username: str = Depends(authenticate), db: Session = Depends(get_db)):
    assets = db.query(models.Asset).order_by(models.Asset.created_at.desc()).all()
    # Serialize with image_url
    result = []
    for a in assets:
        a_dict = {
            "id": a.id,
            "name": a.name,
            "collection": a.collection,
            "fabric_type": a.fabric_type,
            "print_width_cm": a.print_width_cm,
            "repeat_size_cm": a.repeat_size_cm,
            "palette": a.palette,
            "parent_id": a.parent_id,
            "image_path": a.image_path,
            "created_at": a.created_at,
            "image_url": f"http://127.0.0.1:8000/images/{a.image_path}"
        }
        result.append(a_dict)
        
    return {"status": "success", "assets": result}

@app.get("/export/{asset_id}")
async def export_print_package(asset_id: int, username: str = Depends(authenticate), db: Session = Depends(get_db)):
    asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    img_path = os.path.join(PROCESSED_DIR, asset.image_path)
    export_dir = os.path.join(PROCESSED_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)
    out_zip = os.path.join(export_dir, f"texflow_pkg_{asset_id}.zip")
    
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "postprocess", "layout_template.py")
    
    # Run seamless check first as requested
    seam_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "postprocess", "seamless_check.py")
    seam_res = subprocess.run(["python", seam_script, "--input", img_path], capture_output=True, text=True)
    
    if "[FAIL]" in seam_res.stdout:
        raise HTTPException(status_code=400, detail="Asset failed mathematically strict seamless validation. Export blocked.")
    
    # Generate Zip
    subprocess.run([
        "python", script_path, 
        "--body", img_path, 
        "--border", img_path, 
        "--pallu", img_path, 
        "--out", out_zip, 
        "--print-ready",
        "--fabric", asset.fabric_type,
        "--width", str(asset.print_width_cm)
    ])
    
    if os.path.exists(out_zip):
        return FileResponse(out_zip, media_type="application/zip", filename=f"texflow_production_pkg_{asset_id}.zip")
    else:
        raise HTTPException(status_code=500, detail="Failed to generate export package.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
