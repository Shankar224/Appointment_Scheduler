## AI-Powered Appointment Scheduler Assistant

This backend service parses natural language appointment requests from both text and images, converting them into structured scheduling data.

## PLUM-ASSIGNMENT — AI Appointment Scheduler (backend)

This repository contains a small backend service that converts natural-language appointment requests (text or images) into clean, structured scheduling data. It demonstrates practical application of OCR, NLP, and date/time normalization in a modular pipeline useful for chatbots, voice assistants, or calendar integrations.

## Tech stack

- Python 3.8+
- FastAPI (HTTP API)
- spaCy (entity extraction)
- pytesseract + Tesseract OCR (image -> text)
- Pydantic (validation)

## Core capabilities

- Parse free-form appointment requests from text
- Extract text from images and run the same NLP pipeline
- Identify date/time/department and normalize to ISO + timezone
- Return clear statuses: `ok`, `needs_clarification`, or `error`

## Repository highlights

- Modular pipeline: `ocr_module.py`, `nlp_module.py`, `normalize_module.py`, `utils.py` and `schemas.py`.
- Clearly defined API with OpenAPI docs (FastAPI) for easy integration and testing.
- Designed to be testable and replaceable components (swap OCR or NLU easily).

## Setup 

1. Create a virtual environment and activate it (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install Python dependencies and the spaCy model:

```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. Install Tesseract OCR (required for image parsing):

- Windows: download the installer (UB Mannheim builds recommended) — https://github.com/UB-Mannheim/tesseract/wiki
- macOS: `brew install tesseract`
- Debian/Ubuntu: `sudo apt-get install tesseract-ocr`

4. Run the API (development mode):

```powershell
uvicorn app.main:app --reload
```
## Documentation
- The app will be available at [Live-Link](https://appointment-scheduler-41z0.onrender.com/) and the interactive docs at [Swagger UI Docs](https://appointment-scheduler-41z0.onrender.com/docs)
- Postmand Documentation : [Link](https://documenter.getpostman.com/view/44143506/2sB3QJPWHe)

## API usage examples

1) Parse plain text (curl / PowerShell):

```powershell
curl -X POST http://localhost:8000/parse-text \
    -H 'Content-Type: application/json' \
    -d '{"text":"Book dentist next Friday at 3pm"}'
```

2) Parse an image (uploads file and runs OCR):

```powershell
curl -X POST http://localhost:8000/parse-image -F "file=@C:\path\to\image.jpg"
```

Example successful response (abbreviated):

```json
{
    "appointment": {
        "department": "Dentistry",
        "date": "2025-09-26",
        "time": "15:00",
        "tz": "Asia/Kolkata"
    },
    "status": "ok"
}
```

## Architecture and flow

High-level pipeline (module responsibilities):

- OCR (`app/ocr_module.py`) — extracts raw text from uploaded images using pytesseract.
- NLP (`app/nlp_module.py`) — extracts candidate entities (date phrases, times, department/subject) using spaCy and lightweight heuristics.
- Normalization (`app/normalize_module.py`) — converts candidate date/time phrases into ISO date/time strings and applies the default timezone (project default: `Asia/Kolkata`).
- Validation & output (`app/utils.py`, `app/schemas.py`) — validates fields, constructs the final JSON, and returns explicit statuses for downstream systems.




