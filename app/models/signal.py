from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class SignalType(str, enum.Enum):
    NEWS = "news"
    CITIZEN = "citizen"
    EVENT = "event"
    TRAFFIC = "traffic"


class RealTimeSignal(Base):
    __tablename__ = "real_time_signals"

    id = Column(String, primary_key=True, index=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    signal_type = Column(Enum(SignalType))
    weight = Column(Float, default=1.0)
    severity = Column(String, default="low")  # low, medium, high
    source_link = Column(String, nullable=True)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    zone = relationship("Zone", back_populates="real_time_signals")
