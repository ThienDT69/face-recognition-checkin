from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class FaceResult(BaseModel):
    employee_id: UUID
    employee_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]

class RecognitionResponse(BaseModel):
    success: bool
    faces_detected: int
    results: List[FaceResult]
    processing_time: float

class RecognizeImageRequest(BaseModel):
    image_data: str  # base64 encoded

class RegisterFaceRequest(BaseModel):
    employee_id: UUID
    image_data: str  # base64 encoded
