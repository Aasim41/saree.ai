# TexFlow - AI Design & Production Workspace

TexFlow is a professional workspace for digital textile printing. It manages the entire pipeline from design asset ingestion, controlled AI variant generation, mathematical seamless validation, and manufacturer export packaging.

## Features
- **Asset Lineage**: Track parent designs and their AI-generated variants.
- **Upload & Prepare**: Detect dominant colors and define physical fabric requirements.
- **Controlled Variants**: Generate new colourways and scale adjustments safely tied to a parent asset.
- **Production Export**: Export true CMYK, DPI-embedded ZIP packages with machine layout instructions.

## Architecture Notes
- **Database**: Currently using Python's built-in `sqlite3` (no DB driver needed) for rapid MVP prototyping. Scheduled to migrate to PostgreSQL (`psycopg2-binary`) for production scaling.
- **AI Hardware**: Generation requires a CUDA-enabled GPU.

## Setup
(Requires Node.js and Python 3.10+)

**1. Backend:**
```powershell
python -m venv venv
.\venv\Scripts\activate

# IF ON GPU (e.g. RunPod): Install CUDA-enabled torch first, otherwise skip to requirements
pip install torch==2.2.0 --index-url https://download.pytorch.org/whl/cu121

pip install -r requirements.txt
cd app\backend
uvicorn main:app --reload
```

**2. Frontend:**
```powershell
cd app\frontend
npm install
npm run dev
```