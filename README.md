# Saree Design AI

An end-to-end, locally runnable application for AI-assisted textile design.

## Features
- **Strict Data Pipeline**: Component-aware cropping and strict JSON validation for LoRA training.
- **Mathematical Seam Checks**: Automated testing for seamless tile repetition using MAE.
- **Memory-Safe Manufacturer Export**: Exports individual CMYK tiles alongside a layout JSON for standard textile printers, completely avoiding RAM crashes.
- **Designer Interface**: React frontend + FastAPI backend with SQLite asset history.

## Setup Instructions

### 1. Backend (FastAPI)
1. Navigate to the project root: `cd saree-ai`
2. Create virtual environment: `python -m venv venv`
3. Activate it: `.\venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Start server: `cd app/backend` then `uvicorn main:app --reload`

### 2. Frontend (React)
1. Navigate to frontend: `cd app/frontend`
2. Install Node dependencies: `npm install`
3. Start Vite server: `npm run dev`

### 3. Layout / Pipeline Tools
- **Prep Images**: `python data_pipeline/prep_images.py --input_dir data/raw --output_dir data/processed --crop_mode bottom`
- **Seam Check**: `python postprocess/seamless_check.py --input my_tile.jpg`
- **Export Print Package**: `python postprocess/layout_template.py --body b.jpg --border br.jpg --pallu p.jpg --print-ready`