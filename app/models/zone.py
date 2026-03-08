from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
from app.db.database import Base


class Zone(Base):
    __tablename__ = "zones"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    geometry = Column(Geometry('POLYGON'))
    population = Column(Integer)
    base_capacity_police = Column(Integer, default=5)
    base_capacity_fire = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stations = relationship("Station", back_populates="zone")
    historical_calls = relationship("HistoricalCall", back_populates="zone")
    real_time_signals = relationship("RealTimeSignal", back_populates="zone")
    risk_scores = relationship("RiskScore", back_populates="zone")
