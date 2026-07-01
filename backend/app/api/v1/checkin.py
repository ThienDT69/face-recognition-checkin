from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.db.database import get_db
from app.models.checkin import Checkin
from app.models.employee import Employee
from app.schemas.checkin import CheckinResponse

router = APIRouter(prefix="/checkin", tags=["checkin"])

@router.get("/", response_model=List[CheckinResponse])
def list_checkins(
    employee_id: str = None,
    date: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List check-ins with optional filtering"""
    query = db.query(Checkin)
    
    if employee_id:
        query = query.filter(Checkin.employee_id == employee_id)
    
    if date:
        target_date = datetime.strptime(date, "%Y-%m-%d")
        query = query.filter(
            Checkin.check_in_time >= target_date,
            Checkin.check_in_time < target_date + timedelta(days=1)
        )
    
    checkins = query.offset(skip).limit(limit).all()
    return checkins

@router.get("/{checkin_id}", response_model=CheckinResponse)
def get_checkin(checkin_id: str, db: Session = Depends(get_db)):
    """Get specific check-in record"""
    checkin = db.query(Checkin).filter(Checkin.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check-in not found")
    return checkin

@router.post("/manual/{employee_id}")
def manual_checkin(employee_id: str, db: Session = Depends(get_db)):
    """Manual check-in for employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    # Check if already checked in today
    today = datetime.utcnow().date()
    existing = db.query(Checkin).filter(
        Checkin.employee_id == employee_id,
        Checkin.check_in_time >= datetime(today.year, today.month, today.day),
        Checkin.check_out_time == None
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already checked in today")
    
    checkin = Checkin(
        employee_id=employee_id,
        check_in_time=datetime.utcnow(),
        method="manual"
    )
    
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    
    return {"success": True, "checkin_id": str(checkin.id)}

@router.post("/checkout/{employee_id}")
def checkout(employee_id: str, db: Session = Depends(get_db)):
    """Check-out for employee"""
    today = datetime.utcnow().date()
    checkin = db.query(Checkin).filter(
        Checkin.employee_id == employee_id,
        Checkin.check_in_time >= datetime(today.year, today.month, today.day),
        Checkin.check_out_time == None
    ).first()
    
    if not checkin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active check-in found")
    
    checkin.check_out_time = datetime.utcnow()
    db.commit()
    db.refresh(checkin)
    
    return {"success": True, "checkout_time": checkin.check_out_time}

@router.get("/stats/daily")
def daily_stats(
    date: str = None,
    db: Session = Depends(get_db)
):
    """Get daily check-in statistics"""
    if not date:
        date = datetime.utcnow().strftime("%Y-%m-%d")
    
    target_date = datetime.strptime(date, "%Y-%m-%d")
    
    checkins = db.query(Checkin).filter(
        Checkin.check_in_time >= target_date,
        Checkin.check_in_time < target_date + timedelta(days=1)
    ).all()
    
    total_employees = db.query(Employee).filter(Employee.is_active == True).count()
    checked_in = len(set([c.employee_id for c in checkins]))
    
    return {
        "date": date,
        "total_employees": total_employees,
        "checked_in": checked_in,
        "absent": total_employees - checked_in,
        "attendance_rate": round((checked_in / total_employees * 100) if total_employees > 0 else 0, 2)
    }
