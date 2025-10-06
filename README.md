# AI-Powered Appointment Scheduler Assistant

This backend service parses natural language appointment requests from both text and images, converting them into structured scheduling data.

# PLUM-ASS — AI Appointment Scheduler (backend)

Concise, recruiter-friendly summary

This repository contains a small backend service that converts natural-language appointment requests (text or images) into clean, structured scheduling data. It demonstrates practical application of OCR, NLP, and date/time normalization in a modular pipeline useful for chatbots, voice assistants, or calendar integrations.

Why this project matters (for recruiters)

- Shows end-to-end design: ingestion (text/image) → extraction (NLP) → normalization → structured output.
- Practical, production-minded choices: FastAPI for a clean API surface, Pydantic for validation, and modular code that’s easy to test and extend.
- Focus on robustness: ambiguity detection and clear error/status responses make the output safe to use in automated flows.

Tech stack

- Python 3.8+
- FastAPI (HTTP API)
- spaCy (entity extraction)
- pytesseract + Tesseract OCR (image -> text)
- Pydantic (validation)

Core capabilities

- Parse free-form appointment requests from text
- Extract text from images and run the same NLP pipeline
- Identify date/time/department and normalize to ISO + timezone
- Return clear statuses: `ok`, `needs_clarification`, or `error`

Repository highlights (what to mention in interviews)

- Modular pipeline: `ocr_module.py`, `nlp_module.py`, `normalize_module.py`, `utils.py` and `schemas.py`.
- Clearly defined API with OpenAPI docs (FastAPI) for easy integration and testing.
- Designed to be testable and replaceable components (swap OCR or NLU easily).

Setup (quick, copy-paste for reviewers)

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

The app will be available at http://localhost:8000 and the interactive docs at http://localhost:8000/docs

API usage examples

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

Architecture and flow

High-level pipeline (module responsibilities):

- OCR (`app/ocr_module.py`) — extracts raw text from uploaded images using pytesseract.
- NLP (`app/nlp_module.py`) — extracts candidate entities (date phrases, times, department/subject) using spaCy and lightweight heuristics.
- Normalization (`app/normalize_module.py`) — converts candidate date/time phrases into ISO date/time strings and applies the default timezone (project default: `Asia/Kolkata`).
- Validation & output (`app/utils.py`, `app/schemas.py`) — validates fields, constructs the final JSON, and returns explicit statuses for downstream systems.

Design decisions

- FastAPI for automatic OpenAPI docs and developer ergonomics.
- Pydantic schemas for explicit input/output contracts — useful for recruiters evaluating code clarity.
- Modular layout to make unit testing straightforward and to allow swapping components.

Testing & quality suggestions

- Add unit tests for `nlp_module` (entity extraction) and `normalize_module` (date/time conversion). A couple of tests that cover ambiguous inputs and timezone conversions will increase recruiter confidence.
- Add a simple CI pipeline (GitHub Actions) that installs deps, runs linters, and runs tests.

Notes for reviewers

- Default timezone is `Asia/Kolkata` — changeable in `normalize_module.py`.
- If Tesseract OCR is not installed, the `/parse-image` endpoint will return an error explaining the failure.

Next steps I can help with

- Add a short Postman collection or HTTPie examples.
- Add unit tests and a GitHub Actions CI workflow.
- Add a very small front-end demo or a script that simulates typical requests.

If you want any of those, tell me which and I’ll add it.

