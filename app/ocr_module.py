from PIL import Image
import pytesseract
import io
import os

# Configure Tesseract path for Windows
if os.name == 'nt':  # Windows
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_from_bytes(image_bytes: bytes):
    """
    Returns: {raw_text: str, confidence: float}
    Uses pytesseract.image_to_data to compute average word confidence.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # raw text
    raw_text = pytesseract.image_to_string(img, lang='eng')

    # detailed data to estimate confidence
    data = pytesseract.image_to_data(img, lang='eng', output_type=pytesseract.Output.DICT)
    confs = []
    for c in data.get('conf', []):
        try:
            ci = float(c)
        except Exception:
            continue
        # tesseract returns -1 for non-word boxes
        if ci >= 0:
            confs.append(ci)
    
    if len(confs) > 0:
        avg_conf = sum(confs) / len(confs) / 100.0  # normalize to 0..1
        # clamp
        avg_conf = max(0.0, min(1.0, avg_conf))
    else:
        # fallback confidence heuristic
        avg_conf = 0.6

    return {"raw_text": raw_text.strip(), "confidence": round(avg_conf, 2)}


def extract_text_from_fileobj(file_obj):
    """Extract text from a file object containing an image."""
    image_bytes = file_obj.read()
    return extract_text_from_bytes(image_bytes)