# TexFlow - AI Design & Production Workspace

TexFlow is a professional workspace for digital textile printing. It manages the entire pipeline from design asset ingestion, controlled AI variant generation, mathematical seamless validation, and manufacturer export packaging.

## Features
- **Asset Lineage**: Track parent designs and their AI-generated variants.
- **Upload & Prepare**: Detect dominant colors and define physical fabric requirements.
- **Controlled Variants**: Generate new colourways and scale adjustments safely tied to a parent asset.
- **Production Export**: Export true CMYK, DPI-embedded ZIP packages with machine layout instructions.

## Setup
(Requires Node.js and Python 3.10+)

**1. Backend:**
```powershell
python -m venv venv
.\venv\Scripts\activate
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