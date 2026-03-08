from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(String, primary_key=True, index=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    predicted_demand_police = Column(Float, default=0.0)
    predicted_demand_fire = Column(Float, default=0.0)
    signal_multiplier = Column(Float, default=1.0)
    final_risk_score = Column(Float, default=0.0)  # 0-100 scale
    effective_capacity_police = Column(Integer, default=1)
    effective_capacity_fire = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    # Relationships
    zone = relationship("Zone", back_populates="risk_scores")
