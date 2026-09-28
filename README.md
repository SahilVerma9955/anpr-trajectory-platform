# ANPR Trajectory Platform

This repository is an MVP for an Indian traffic ANPR and vehicle-trajectory platform. It is designed to work locally first and to be deployable to IBM Cloud afterward.

Important dataset note
- The Kaggle dataset is external and may not contain license-plate bounding-box labels.
- We do not assume the dataset structure or annotation format ahead of time.
- The project includes inspection code that checks the real files and adapts to the actual dataset layout.
- Vehicle detection and plate OCR are implemented as pretrained-baseline pipelines unless manually labelled training data is available.

Project goals
- Read Indian traffic videos from `data/raw/`
- Extract frames and video metadata
- Detect vehicles using Ultralytics YOLO
- Track vehicles across frames
- Try plate localization and OCR using pretrained models as a baseline
- Support future custom plate detection trained on YOLO-format labels
- Aggregate traffic analytics and expose them through FastAPI
- Show results in a React dashboard
- Provide local SQLite storage and optional PostgreSQL support

Quick start
1. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
   Windows:
   ```bash
   .venv\Scripts\activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Download the Kaggle dataset
   ```bash
   python scripts/download_kaggle_dataset.py
   ```
4. Inspect the real dataset structure
   ```bash
   python scripts/inspect_dataset.py
   ```
5. Initialize the SQLite database
   ```bash
   python scripts/init_db.py
   ```
6. Run the detection pipeline
   ```bash
   python scripts/run_pipeline.py --input data/raw
   ```
7. Start the API
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```
8. Start the frontend
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

Expected URLs
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Frontend: http://localhost:5173

Dataset and training safety
- This project never pretends that plate training data exists unless actual annotation files are present and validated.
- If the dataset contains no plate labels, the pipeline falls back to pretrained detection + OCR as a baseline.
- Production ANPR accuracy requires manually labelled Indian plate data, evaluation on a proper test set, and real calibration.

Repository structure
- `scripts/` contains dataset inspection, preprocessing, detection, and pipeline runners.
- `src/` contains backend modules for video processing, detection, OCR, tracking, analytics, database, and API.
- `frontend/` contains the React dashboard.
- `config/` contains YAML configuration for cameras, models, and system defaults.

License and compliance
- Obtain permission before processing CCTV or ANPR data.
- Use this project only for lawful, privacy-aware traffic analysis in authorized environments.
- Do not use the prototype for unsupervised enforcement, automated arrests, or denial-of-service decisions.

Next steps
- Inspect the actual Kaggle files.
- Use the resulting `data/processed/dataset_report.json` as the source of truth for dataset capabilities.
- Train a custom plate detector only when local, manually labelled plate annotations are available.
