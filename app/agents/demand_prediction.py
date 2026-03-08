import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm import Session
from app.models.call import HistoricalCall, CallType
from app.models.risk import RiskScore
from app.models.zone import Zone
import os


class DemandPredictionAgent:
    """
    Forecasts emergency call demand per zone for the next 6 hours.

    PREDICTION LOGIC:
    - Uses last 30 days of historical calls for the zone
    - Applies time-of-day weighting (evenings/nights score higher)
    - Applies day-of-week weighting (weekends score higher for police)
    - Returns demand as calls-per-6h window, not a raw rolling count
      (old rolling_24h_demand * 0.6 was producing ~10-11 for all zones
       regardless of actual activity, making risk scores undifferentiated)
    """

    def __init__(self, db: Session):
        self.db    = db
        os.makedirs("models/", exist_ok=True)

    # Time-of-day multipliers (hour → weight)
    # Emergencies peak in evenings; quiet overnight
    TIME_WEIGHTS = {
        range(0,  6):  0.6,   # midnight–6am: low
        range(6,  12): 0.9,   # morning: moderate
        range(12, 18): 1.0,   # afternoon: baseline
        range(18, 22): 1.3,   # evening: elevated
        range(22, 24): 1.1,   # late night: slightly elevated
    }

    # Day-of-week multipliers (0=Monday … 6=Sunday)
    DAY_WEIGHTS = {
        0: 0.9, 1: 0.9, 2: 0.9, 3: 1.0,
        4: 1.1, 5: 1.3, 6: 1.2,  # Fri/Sat/Sun higher
    }

    def _get_time_weight(self, hour: int) -> float:
        for r, w in self.TIME_WEIGHTS.items():
            if hour in r:
                return w
        return 1.0

    def predict_demand(self, zone_id: str, horizon_hours: int = 6) -> Dict[str, float]:
        calls = self.db.query(HistoricalCall).filter(
            HistoricalCall.zone_id == zone_id,
            HistoricalCall.timestamp >= datetime.utcnow() - timedelta(days=30),
        ).all()

        zone = self.db.query(Zone).filter(Zone.id == zone_id).first()

        if not calls:
            # Baseline: 40% of zone capacity as expected demand
            return {
                "predicted_police": round((zone.base_capacity_police or 8) * 0.4, 2),
                "predicted_fire":   round((zone.base_capacity_fire or 5) * 0.4, 2),
            }

        now         = datetime.utcnow()
        time_weight = self._get_time_weight(now.hour)
        day_weight  = self.DAY_WEIGHTS.get(now.weekday(), 1.0)

        police_calls = [c for c in calls if c.call_type == CallType.POLICE]
        fire_calls   = [c for c in calls if c.call_type == CallType.FIRE]

        # Average calls per 6h window over last 30 days
        # 30 days = 120 × 6h windows
        windows = max(1, 30 * 24 / horizon_hours)

        police_rate = len(police_calls) / windows
        fire_rate   = len(fire_calls)   / windows

        # Apply time and day weights
        police_pred = police_rate * time_weight * day_weight
        fire_pred   = fire_rate   * time_weight * day_weight

        return {
            "predicted_police": round(max(0.1, police_pred), 4),
            "predicted_fire":   round(max(0.1, fire_pred),   4),
        }

    def run(self):
        zones = self.db.query(Zone).all()

        for zone in zones:
            predictions = self.predict_demand(zone.id)

            risk_score = self.db.query(RiskScore).filter(
                RiskScore.zone_id == zone.id
            ).first()

            if not risk_score:
                risk_score = RiskScore(id=f"risk_{zone.id}", zone_id=zone.id)
                self.db.add(risk_score)

            risk_score.predicted_demand_police = predictions["predicted_police"]
            risk_score.predicted_demand_fire   = predictions["predicted_fire"]

        self.db.commit()