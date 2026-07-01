from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import io
from PIL import Image

from app.db.database import get_db
from app.schemas.recognition import RecognitionResponse, FaceResult
from app.services.face_recognition import FaceRecognitionService
from app.models.employee import Employee
from app.models.face_embedding import FaceEmbedding

router = APIRouter(prefix="/recognize", tags=["recognition"])

def get_face_service():
    from app.main import face_service as _face_service
    return _face_service

@router.post("/image", response_model=RecognitionResponse)
async def recognize_from_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Recognize faces from uploaded image"""
    try:
        face_service = get_face_service()
        
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        import numpy as np
        image_array = np.array(image)
        
        # Detect and recognize faces
        import time
        start_time = time.time()
        
        faces = face_service.detect_faces(image_array)
        results = []
        
        for face in faces:
            embedding = face_service.get_embedding(image_array, face)
            
            # Find matching employee
            match = face_service.find_match(embedding, db)
            
            if match:
                results.append(FaceResult(
                    employee_id=match['employee_id'],
                    employee_name=match['name'],
                    confidence=match['confidence'],
                    bbox=face.bbox.tolist()
                ))
        
        processing_time = time.time() - start_time
        
        return RecognitionResponse(
            success=True,
            faces_detected=len(faces),
            results=results,
            processing_time=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/register/{employee_id}")
async def register_face(
    employee_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Register employee face for recognition"""
    try:
        # Check employee exists
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        
        face_service = get_face_service()
        
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        import numpy as np
        image_array = np.array(image)
        
        # Detect face
        faces = face_service.detect_faces(image_array)
        if not faces:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No face detected in image")
        
        # Get embedding from best face
        best_face = max(faces, key=lambda x: x.det_score)
        embedding = face_service.get_embedding(image_array, best_face)
        
        # Save embedding to database
        image_path = f"uploads/{employee_id}_{file.filename}"
        
        # Save image
        import os
        os.makedirs("uploads", exist_ok=True)
        with open(image_path, "wb") as f:
            f.write(contents)
        
        # Create embedding record
        face_embedding = FaceEmbedding(
            employee_id=employee_id,
            embedding=embedding.tolist(),
            image_path=image_path,
            quality_score=float(best_face.det_score)
        )
        
        db.add(face_embedding)
        db.commit()
        
        return {
            "success": True,
            "message": "Face registered successfully",
            "employee_id": str(employee_id),
            "quality_score": float(best_face.det_score)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
