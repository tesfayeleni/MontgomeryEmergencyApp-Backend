from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.db.database import get_db
from app.auth.middleware import get_current_user, require_role
from app.models.user import UserRole
from app.models.zone import Zone
from app.models.report import CitizenReport, ReportType
from app.models.event import Event
import uuid
from datetime import datetime

router = APIRouter(prefix="/citizen", tags=["citizen"])


class CitizenReportRequest(BaseModel):
    report_type: str  # crowding, hazard, suspicious_activity
    latitude: float
    longitude: float
    severity: str = "low"  # low, medium, high
    description: str
    photo_url: str | None = None


class EventSubmissionRequest(BaseModel):
    title: str
    latitude: float
    longitude: float
    event_date: str  # ISO format
    expected_attendance: int
    description: str = ""


class PublicSignalResponse(BaseModel):
    zone_id: str
    zone_name: str
    risk_level: str  # low, medium, high


@router.post("/report")
async def submit_report(
    request: CitizenReportRequest,
    current_user: dict = Depends(require_role(
        UserRole.RESIDENT,
        UserRole.BUSINESS_OWNER,
        UserRole.EVENT_ORGANIZER,
    )),
    db: Session = Depends(get_db),
):
    """Submit non-emergency report from citizen"""
    try:
        report_type = ReportType(request.report_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid report type",
        )
    
    report = CitizenReport(
        id=str(uuid.uuid4()),
        user_id=current_user["user_id"],
        report_type=report_type,
        latitude=request.latitude,
        longitude=request.longitude,
        location=f"POINT({request.longitude} {request.latitude})",
        severity=request.severity,
        description=request.description,
        photo_url=request.photo_url,
    )
    
    db.add(report)
    db.commit()
    
    return {
        "id": report.id,
        "status": "submitted",
        "message": "Thank you for your report",
    }


@router.post("/event")
async def submit_event(
    request: EventSubmissionRequest,
    current_user: dict = Depends(require_role(UserRole.EVENT_ORGANIZER)),
    db: Session = Depends(get_db),
):
    """Submit event notification"""
    event = Event(
        id=str(uuid.uuid4()),
        organizer_id=current_user["user_id"],
        title=request.title,
        latitude=request.latitude,
        longitude=request.longitude,
        location=f"POINT({request.longitude} {request.latitude})",
        event_date=datetime.fromisoformat(request.event_date),
        expected_attendance=request.expected_attendance,
        description=request.description,
    )
    
    db.add(event)
    db.commit()
    
    # Simulate risk impact
    simulated_risk_increase = min(request.expected_attendance / 100, 20)
    
    return {
        "id": event.id,
        "status": "submitted",
        "simulated_risk_increase": f"+{simulated_risk_increase:.1f}%",
        "message": "Event submitted successfully",
    }


@router.get("/public-feed")
async def get_public_feed(db: Session = Depends(get_db)):
    """Get public safety feed visible to everyone"""
    from app.models.signal import RealTimeSignal
    from datetime import datetime as dt
    
    # Get public signals (only high severity)
    public_signals = db.query(RealTimeSignal).filter(
        RealTimeSignal.severity == "high",
        # RealTimeSignal.expires_at > dt.utcnow(),
    ).all()
    
    # Get recent citizen reports
    recent_reports = db.query(CitizenReport).filter(
        CitizenReport.verified == "verified",
    ).order_by(CitizenReport.created_at.desc()).limit(10).all()
    
    return {
        "alerts": [
            {
                "type": "news_alert",
                "zone_id": s.zone_id,
                "zone_name": s.zone.name,
                "title": s.title,
                "severity": s.severity,
                "timestamp": s.created_at.isoformat(),
            }
            for s in public_signals
        ],
        "verified_reports": [
            {
                "type": "verified_report",
                "report_type": r.report_type.value,
                "severity": r.severity,
                "created_at": r.created_at.isoformat(),
            }
            for r in recent_reports
        ],
    }
