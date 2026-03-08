from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class CallType(str, enum.Enum):
    POLICE = "police"
    FIRE = "fire"


class HistoricalCall(Base):
    __tablename__ = "historical_calls"

    id = Column(String, primary_key=True, index=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    timestamp = Column(DateTime, index=True)
    call_type = Column(Enum(CallType))
    response_time = Column(Float)  # in minutes
    severity = Column(Integer, default=1)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    zone = relationship("Zone", back_populates="historical_calls")
