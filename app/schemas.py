from pydantic import BaseModel
from typing import Optional, Dict, Any


class OCRResult(BaseModel):
    raw_text: str
    confidence: float


class EntitiesResult(BaseModel):
    entities: Dict[str, Optional[str]]
    entities_confidence: float


class NormalizationResult(BaseModel):
    normalized: Optional[Dict[str, str]] = None
    normalization_confidence: Optional[float] = None
    status: Optional[str] = None
    message: Optional[str] = None


class FinalAppointment(BaseModel):
    appointment: Optional[Dict[str, str]] = None
    status: str
    message: Optional[str] = None