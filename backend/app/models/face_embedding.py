from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid
from datetime import datetime

from app.db.database import Base

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)  # 512-dim vector
    image_path = Column(String(255), nullable=False)
    quality_score = Column(Float)  # Face quality score
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FaceEmbedding for employee_id {self.employee_id}>"
