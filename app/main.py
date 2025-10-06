from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Dict, Optional
import datetime

from .ocr_module import extract_text_from_fileobj
from .nlp_module import extract_entities
from .normalize_module import normalize
from .utils import apply_guardrails_and_build
from .schemas import OCRResult, EntitiesResult, NormalizationResult, FinalAppointment

description = """
# AI Appointment Scheduler API

This API provides intelligent appointment scheduling capabilities through both text and image inputs.
It uses advanced NLP and OCR techniques to extract and normalize appointment date and time information.

## Features

* 📝 Text-based appointment parsing
* 🖼️ Image-based appointment parsing with OCR
* 🕒 Date and time normalization
* 🌐 Timezone support
"""

tags_metadata = [
    {
        "name": "text",
        "description": "Operations with text-based appointment requests",
    },
    {
        "name": "image",
        "description": "Operations with image-based appointment requests using OCR",
    },
]

app = FastAPI(
    title="AI Appointment Scheduler API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    }
)

class TextIn(BaseModel):
    text: str
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Schedule an appointment for tomorrow at 2pm"
            }
        }

@app.post(
    "/parse-text",
    response_model=FinalAppointment,
    tags=["text"],
    summary="Parse appointment details from text",
    description="""
    Extracts appointment information from plain text input.
    
    The endpoint performs the following steps:
    1. Processes the input text
    2. Extracts date and time entities
    3. Normalizes the extracted information
    4. Returns a structured appointment object
    """,
    response_description="Processed appointment information with normalized date and time"
)
async def parse_text(text_in: TextIn):
    """
    Parse appointment details from text input.
    
    Args:
        text_in (TextIn): The input text containing appointment information
        
    Returns:
        FinalAppointment: Processed and normalized appointment information
        
    Raises:
        HTTPException: If the text cannot be processed
    """
    text = text_in.text
    ocr_result = {"raw_text": text, "confidence": 1.0}
    entities = extract_entities(text)
    normalization = normalize(entities['entities'].get('date_phrase'), entities['entities'].get('time_phrase'))
    final = apply_guardrails_and_build(ocr_result, entities, normalization)
    return JSONResponse(content=final)

@app.post(
    "/parse-image",
    response_model=FinalAppointment,
    tags=["image"],
    summary="Parse appointment details from an image",
    description="""
    Extracts appointment information from an uploaded image using OCR.
    
    The endpoint performs the following steps:
    1. Validates the uploaded file is an image
    2. Performs OCR to extract text
    3. Extracts date and time entities from the text
    4. Normalizes the extracted information
    5. Returns a structured appointment object
    
    Supported image formats:
    * PNG
    * JPEG/JPG
    * TIFF
    * BMP
    """,
    response_description="Processed appointment information with normalized date and time"
)
async def parse_image(
    image: UploadFile = File(
        ...,
        description="The image file containing appointment text"
    )
):
    """
    Parse appointment details from an image file.
    
    Args:
        image (UploadFile): The uploaded image file containing appointment information
        
    Returns:
        FinalAppointment: Processed and normalized appointment information
        
    Raises:
        HTTPException: If the file is not an image or if processing fails
    """
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (PNG, JPEG, TIFF, or BMP)"
        )
    
    try:
        # Read the file content
        contents = await image.read()
        
        # Process the image contents directly
        from .ocr_module import extract_text_from_bytes
        ocr_result = extract_text_from_bytes(contents)
        
        # Process the extracted text
        entities = extract_entities(ocr_result['raw_text'])
        normalization = normalize(
            entities['entities'].get('date_phrase'),
            entities['entities'].get('time_phrase')
        )
        final = apply_guardrails_and_build(ocr_result, entities, normalization)
        
        return JSONResponse(content=final)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )
    finally:
        await image.close()

@app.get(
    "/health",
    tags=["health"],
    summary="Check API health",
    description="Returns the health status of the API",
    response_description="Health check response"
)
async def health_check():
    """
    Perform a health check on the API.
    
    Returns:
        dict: A dictionary containing the status of the API
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags
    )

    # Custom documentation customization can be done here
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)