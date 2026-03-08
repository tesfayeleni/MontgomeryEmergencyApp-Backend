from sqlalchemy import Column, String, DateTime, Integer, Float, Text
from datetime import datetime
from app.db.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    organizer_id = Column(String)  # References users table implicitly
    title = Column(String, index=True)
    location = Column(String)  # GeoJSON point
    latitude = Column(Float)
    longitude = Column(Float)
    event_date = Column(DateTime)
    expected_attendance = Column(Integer)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
