from fastapi import FastAPI, UploadFile, Form, Depends, HTTPException, status, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uvicorn
import os
import sys
import uuid
import subprocess
import tempfile
import shutil
import logging
from typing import Optional
from dotenv import load_dotenv
from PIL import Image, ImageDraw
from colorthief import ColorThief

sys.path.insert(0, root_dir)

from database import get_db, engine
import models
import schemas
from inference.generate import generate_variant_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
env_path = os.path.join(root_dir, ".env")
load_dotenv(env_path)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024

app = FastAPI(title="TexFlow Workspace")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
        "http://localhost:5175", "http://127.0.0.1:5175",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

security = HTTPBasic()
AUTH_USER = os.getenv("AUTH_USER", "admin")
AUTH_PASS = os.getenv("AUTH_PASS", "admin")

RAW_DIR = os.path.join(root_dir, "data", "raw_images")
PROCESSED_DIR = os.path.join(root_dir, "data", "processed")
POSTPROCESS_DIR = os.path.join(root_dir, "postprocess")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
app.mount("/images/raw", StaticFiles(directory=RAW_DIR), name="raw_images")
app.mount("/images/processed", StaticFiles(directory=PROCESSED_DIR), name="processed_images")


def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != AUTH_USER or credentials.password != AUTH_PASS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def extract_dominant_colors(image_path: str) -> str:
    try:
        color_thief = ColorThief(image_path)
        palette = color_thief.get_palette(color_count=3)
        hex_colors = [f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}" for c in palette]
        return ", ".join(hex_colors)
    except Exception as exc:
        logger.warning("Color extraction failed: %s", exc)
        return "#ffffff, #000000"


def validate_image_file(file: UploadFile, content: bytes) -> None:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds 20 MB upload limit")
    try:
        from io import BytesIO
        img = Image.open(BytesIO(content))
        img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file")


def run_script(script_name: str, args: list[str]) -> subprocess.CompletedProcess:
    script_path = os.path.join(POSTPROCESS_DIR, script_name)
    result = subprocess.run(
        [sys.executable, script_path, *args],
        capture_output=True,
        text=True,
        cwd=POSTPROCESS_DIR,
        timeout=120,
    )
    if result.returncode != 0:
        logger.error("%s stderr: %s", script_name, result.stderr)
    return result


def design_to_dict(d: models.Design) -> dict:
    return {
        "id": d.id,
        "name": d.name or d.filename,
        "filename": d.filename,
        "fabric_type": d.fabric_type,
        "dominant_colors": d.dominant_colors,
        "palette": d.dominant_colors,
        "print_width_cm": d.print_width_cm,
        "repeat_size_cm": d.repeat_size_cm,
        "caption": d.caption,
        "uploaded_at": d.uploaded_at,
        "image_url": f"{API_BASE_URL}/images/raw/{d.filename}",
        "type": "design",
        "parent_id": None,
    }


def variant_to_dict(v: models.Variant, parent: Optional[models.Design] = None) -> dict:
    return {
        "id": v.id,
        "name": f"Variant of {parent.name if parent and parent.name else parent.filename if parent else v.parent_id}",
        "filename": v.filename,
        "fabric_type": parent.fabric_type if parent else None,
        "dominant_colors": None,
        "palette": None,
        "print_width_cm": parent.print_width_cm if parent else None,
        "repeat_size_cm": parent.repeat_size_cm if parent else None,
        "caption": v.prompt_used,
        "created_at": v.created_at,
        "image_url": f"{API_BASE_URL}/images/processed/{v.filename}",
        "type": "variant",
        "parent_id": v.parent_id,
        "prompt_used": v.prompt_used,
        "lora_used": v.lora_used,
    }


@app.on_event("startup")
def ensure_tables():
    models.Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload", response_model=schemas.DesignResponse)
async def upload_asset(
    fabric_type: str = Form(...),
    file: UploadFile = File(...),
    name: str = Form(""),
    print_width_cm: Optional[int] = Form(None),
    repeat_size_cm: Optional[int] = Form(None),
    username: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    content = await file.read()
    validate_image_file(file, content)

    asset_uuid = str(uuid.uuid4())
    filename = f"{asset_uuid}_{file.filename}"
    filepath = os.path.join(RAW_DIR, filename)

    with open(filepath, "wb") as buffer:
        buffer.write(content)

    palette = extract_dominant_colors(filepath)

    db_design = models.Design(
        name=name or None,
        filename=filename,
        dominant_colors=palette,
        fabric_type=fabric_type,
        print_width_cm=print_width_cm,
        repeat_size_cm=repeat_size_cm,
        caption="[BLIP-2 Auto-Caption Pending]",
    )
    db.add(db_design)
    db.commit()
    db.refresh(db_design)

    response = schemas.DesignResponse.model_validate(db_design)
    response.image_url = f"{API_BASE_URL}/images/raw/{db_design.filename}"
    return response


@app.post("/generate-variant/{parent_id}", response_model=schemas.VariantResponse)
async def generate_variant(
    parent_id: int,
    prompt: str = Form(""),
    lora: str = Form(""),
    username: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    parent = db.query(models.Design).filter(models.Design.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent design not found")

    effective_prompt = prompt or parent.caption or (
        f"Traditional saree textile design, {parent.fabric_type or 'silk'}, "
        f"colors: {parent.dominant_colors or 'rich tones'}, seamless pattern"
    )

    image = generate_variant_image(prompt=effective_prompt, lora=lora)

    if image is None:
        img_path = os.path.join(RAW_DIR, parent.filename)
        base_img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(base_img)
        draw.rectangle([0, 0, 200, 50], fill="black")
        draw.text((10, 10), "VARIANT (mock)", fill="white")
        image = base_img

    variant_uuid = str(uuid.uuid4())
    filename = f"variant_{variant_uuid}.jpg"
    filepath = os.path.join(PROCESSED_DIR, filename)
    image.save(filepath, format="JPEG", quality=90)

    variant_asset = models.Variant(
        parent_id=parent_id,
        prompt_used=effective_prompt,
        lora_used=lora or "saree_lora",
        filename=filename,
    )

    db.add(variant_asset)
    db.commit()
    db.refresh(variant_asset)

    response = schemas.VariantResponse.model_validate(variant_asset)
    response.image_url = f"{API_BASE_URL}/images/processed/{variant_asset.filename}"
    return response


@app.get("/assets")
async def get_assets(username: str = Depends(authenticate), db: Session = Depends(get_db)):
    designs = db.query(models.Design).order_by(models.Design.uploaded_at.desc()).all()
    variants = db.query(models.Variant).order_by(models.Variant.created_at.desc()).all()
    design_map = {d.id: d for d in designs}

    result = [design_to_dict(d) for d in designs]
    for v in variants:
        result.append(variant_to_dict(v, design_map.get(v.parent_id)))

    result.sort(key=lambda x: x.get("created_at") or x.get("uploaded_at"), reverse=True)
    return {"status": "success", "assets": result}


@app.get("/export/{variant_id}")
async def export_print_package(
    variant_id: int,
    username: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    variant = db.query(models.Variant).filter(models.Variant.id == variant_id).first()
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")

    parent = db.query(models.Design).filter(models.Design.id == variant.parent_id).first()
    img_path = os.path.join(PROCESSED_DIR, variant.filename)
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Variant image file not found")

    export_dir = os.path.join(PROCESSED_DIR, "exports")
    os.makedirs(export_dir, exist_ok=True)
    out_zip = os.path.join(export_dir, f"texflow_pkg_variant_{variant_id}.zip")

    existing = (
        db.query(models.Export)
        .filter(models.Export.variant_id == variant_id, models.Export.file_path == out_zip)
        .first()
    )
    if existing and os.path.exists(out_zip):
        return FileResponse(
            out_zip,
            media_type="application/zip",
            filename=f"texflow_production_pkg_var{variant_id}.zip",
        )

    temp_dir = tempfile.mkdtemp(prefix="texflow_seam_")
    try:
        seam_output = os.path.join(temp_dir, "seamless_check.jpg")
        seam_res = run_script(
            "seamless_check.py",
            ["--input", img_path, "--output", seam_output, "--tolerance", "15.0"],
        )
        if "[FAIL]" in seam_res.stdout:
            raise HTTPException(
                status_code=400,
                detail="Variant failed seamless validation. Export blocked.",
            )

        fabric = parent.fabric_type if parent and parent.fabric_type else "Silk"
        width = str(parent.print_width_cm if parent and parent.print_width_cm else 120)

        layout_res = run_script(
            "layout_template.py",
            [
                "--body", img_path,
                "--border", img_path,
                "--pallu", img_path,
                "--out", out_zip,
                "--print-ready",
                "--fabric", fabric,
                "--width", width,
            ],
        )
        if layout_res.returncode != 0 or not os.path.exists(out_zip):
            raise HTTPException(status_code=500, detail="Failed to generate export package.")

        db_export = models.Export(
            variant_id=variant_id, dpi=300, color_mode="CMYK", file_path=out_zip
        )
        db.add(db_export)
        db.commit()

        return FileResponse(
            out_zip,
            media_type="application/zip",
            filename=f"texflow_production_pkg_var{variant_id}.zip",
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
