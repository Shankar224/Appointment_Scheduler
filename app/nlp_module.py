import spacy
import re
from typing import Dict

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # If model not found, download it
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Department mapping
DEPARTMENT_KEYWORDS = {
    "dentist": "Dentistry",
    "dental": "Dentistry",
    "doctor": "General Medicine",
    "physician": "General Medicine",
    "eye": "Ophthalmology",
    "opthal": "Ophthalmology",
    "cardiac": "Cardiology",
    "heart": "Cardiology",
    "cardio": "Cardiology",
    "cardiologist": "Cardiology",
    "derma": "Dermatology",
    "skin": "Dermatology",
    "dermatologist": "Dermatology",
    "dermatology": "Dermatology",
    "neuro": "Neurology",
    "neurologist": "Neurology",
    "brain": "Neurology",
    "ortho": "Orthopedics",
    "orthopedic": "Orthopedics",
    "bone": "Orthopedics",
    "ent": "ENT",
    "ear": "ENT",
    "nose": "ENT",
    "throat": "ENT",
    "gastro": "Gastroenterology",
    "stomach": "Gastroenterology",
    "gastroenterologist": "Gastroenterology",
    "pediatric": "Pediatrics",
    "child": "Pediatrics",
    "children": "Pediatrics",
    "gynec": "Gynecology",
    "gynaecologist": "Gynecology",
    "obgyn": "Gynecology",
    "psych": "Psychiatry",
    "psychiatrist": "Psychiatry",
    "mental": "Psychiatry"
}

# Regex patterns for date/time
DATE_TIME_REGEXES = [
    r"(next|this) (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
    r"(tomorrow|today|tonight)",
    r"(\d{1,2}(?:st|nd|rd|th)? (?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)(?:\s*,?\s*\d{4})?)",
]

TIME_REGEX = r"\b(?:at\s+)?(\d{1,2})(?::?\d{2})?\s*(?:am|pm|AM|PM)\b"

def extract_entities_from_text(text: str) -> Dict:
    """Extract date, time and department entities from text."""
    if not text:
        return {"date_phrase": None, "time_phrase": None, "department": None}

    text_l = text.lower()

    # department detection by keyword
    department = None
    for key, normalized in DEPARTMENT_KEYWORDS.items():
        if re.search(r"\b" + re.escape(key) + r"\b", text_l):
            department = normalized
            break

    # try spaCy for DATE/TIME entities (but often spaCy returns relative words like "next Friday")
    doc = nlp(text)
    date_phrase = None
    time_phrase = None
    for ent in doc.ents:
        if ent.label_ in ("DATE",) and date_phrase is None:
            date_phrase = ent.text
        if ent.label_ in ("TIME",) and time_phrase is None:
            time_phrase = ent.text

    # If not found via spaCy, try regex patterns
    if not date_phrase:
        for rx in DATE_TIME_REGEXES:
            m = re.search(rx, text_l)
            if m:
                date_phrase = m.group(1) if m.groups() else m.group(0)
                break

    if not time_phrase:
        m = re.search(TIME_REGEX, text_l)
        if m:
            time_phrase = m.group(0)

    return {"date_phrase": date_phrase, "time_phrase": time_phrase, "department": department}

def extract_entities(text: str) -> Dict:
    """
    Wraps extraction and returns EntitiesResult-like dict with a confidence score heuristic.
    """
    ent_map = extract_entities_from_text(text)

    # heuristic confidence: start at 0.5; add points for each found entity
    conf = 0.5
    if ent_map.get("date_phrase"):
        conf += 0.2
    if ent_map.get("time_phrase"):
        conf += 0.2
    if ent_map.get("department"):
        conf += 0.1

    conf = min(0.99, conf)

    return {"entities": ent_map, "entities_confidence": round(conf, 2)}
