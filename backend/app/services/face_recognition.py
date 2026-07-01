import insightface
import numpy as np
from typing import Dict, List, Optional
from scipy.spatial.distance import cosine
from sqlalchemy.orm import Session

from app.models.face_embedding import FaceEmbedding
from app.models.employee import Employee
from app.config import get_settings

settings = get_settings()

class FaceRecognitionService:
    """Face recognition service using InsightFace"""
    
    def __init__(self, model_name: str = "buffalo_l"):
        """Initialize face recognition model"""
        self.model_name = model_name
        self.app = insightface.app.FaceAnalysis(
            name=model_name,
            providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
        )
        self.app.prepare(ctx_id=0, det_thresh=0.5, det_size=(640, 640))
        print(f"✅ Face Recognition Model '{model_name}' loaded successfully")
    
    def detect_faces(self, image: np.ndarray) -> List:
        """
        Detect faces in image
        
        Args:
            image: numpy array of shape (H, W, 3)
        
        Returns:
            List of face objects with detection info
        """
        try:
            faces = self.app.get(image)
            return faces
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def get_embedding(self, image: np.ndarray, face) -> np.ndarray:
        """
        Get face embedding from detected face
        
        Args:
            image: numpy array of shape (H, W, 3)
            face: face object from detection
        
        Returns:
            512-dimensional face embedding
        """
        return face.embedding
    
    def find_match(
        self,
        embedding: np.ndarray,
        db: Session,
        threshold: float = None
    ) -> Optional[Dict]:
        """
        Find matching employee for given face embedding
        
        Args:
            embedding: 512-dim face embedding
            db: database session
            threshold: confidence threshold (default from settings)
        
        Returns:
            Dict with employee info and confidence, or None
        """
        if threshold is None:
            threshold = settings.CONFIDENCE_THRESHOLD
        
        # Get all stored embeddings
        stored_embeddings = db.query(FaceEmbedding).all()
        
        best_match = None
        best_confidence = 0
        
        for stored in stored_embeddings:
            # Calculate similarity
            stored_emb = np.array(stored.embedding)
            distance = cosine(embedding, stored_emb)
            
            # Convert distance to confidence score (0-1)
            # Lower distance = higher confidence
            confidence = 1 - distance
            
            if confidence > best_confidence and confidence >= threshold:
                best_confidence = confidence
                best_match = stored
        
        if best_match:
            employee = db.query(Employee).filter(
                Employee.id == best_match.employee_id
            ).first()
            
            return {
                "employee_id": str(best_match.employee_id),
                "name": employee.name if employee else "Unknown",
                "confidence": float(best_confidence)
            }
        
        return None
    
    def cleanup(self):
        """Cleanup resources"""
        pass
