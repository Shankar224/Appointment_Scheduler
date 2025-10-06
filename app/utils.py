from .nlp_module import extract_entities
from .normalize_module import normalize


def apply_guardrails_and_build(ocr_result, entities_result, normalization_result):
    """Combines OCR -> Entities -> Normalization outputs into final appointment JSON with guardrails."""
    ents = entities_result.get('entities', {})

    # If normalization returned a needs_clarification
    if isinstance(normalization_result, dict) and normalization_result.get('status') == 'needs_clarification':
        return {"status": "needs_clarification", "message": normalization_result.get('message')}

    if not ents.get('department'):
        return {"status": "needs_clarification", "message": "Ambiguous or missing department"}

    if not normalization_result.get('normalized'):
        return {"status": "needs_clarification", "message": "Ambiguous or missing date/time"}

    appointment = {
        "department": ents['department'],
        "date": normalization_result['normalized']['date'],
        "time": normalization_result['normalized']['time'],
        "tz": normalization_result['normalized']['tz']
    }

    return {"appointment": appointment, "status": "ok"}