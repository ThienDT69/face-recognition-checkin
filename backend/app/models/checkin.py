from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from app.db.database import Base

class Checkin(Base):
    __tablename__ = "checkins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    check_in_time = Column(DateTime, nullable=False)
    check_out_time = Column(DateTime)
    method = Column(String(50), default="camera")  # camera, upload, manual
    confidence = Column(Float)  # Recognition confidence
    image_path = Column(String(255))  # Path to captured/uploaded image
    is_late = Column(Integer, default=0)  # 0=on-time, 1=late
    notes = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Checkin employee_id={self.employee_id} check_in={self.check_in_time}>"
