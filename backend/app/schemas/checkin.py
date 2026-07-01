from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class CheckinBase(BaseModel):
    employee_id: UUID
    method: str = "camera"
    confidence: Optional[float] = None

class CheckinCreate(CheckinBase):
    pass

class CheckinResponse(CheckinBase):
    id: UUID
    check_in_time: datetime
    check_out_time: Optional[datetime]
    is_late: int
    created_at: datetime
    
    class Config:
        from_attributes = True
