from sqlalchemy import Column, String, DateTime, Float, Text, Enum
from datetime import datetime
import enum
from app.db.database import Base


class ReportType(str, enum.Enum):
    CROWDING = "crowding"
    HAZARD = "hazard"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    OTHER = "other"


class CitizenReport(Base):
    __tablename__ = "citizen_reports"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String)  # References users table implicitly
    report_type = Column(Enum(ReportType))
    location = Column(String)  # GeoJSON point
    latitude = Column(Float)
    longitude = Column(Float)
    severity = Column(String, default="low")  # low, medium, high
    description = Column(Text)
    photo_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    verified = Column(String, default="unverified")  # unverified, verified, dismissed
