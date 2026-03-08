from sqlalchemy.orm import Session
from app.models.risk import RiskScore
from app.models.zone import Zone
from datetime import datetime


class RiskScoringAgent:
    """
    Calculates final risk scores.

    FORMULA FIX:
    - Old: raw_score = (demand * multiplier) / capacity * 100
      With capacity=1 (no stations found) → always 100 (CRITICAL)
    - New: capacity falls back to zone.base_capacity_* instead of 1
      so zones without station assignments get a realistic baseline,
      not an artificially maxed score.

    SCORE INTERPRETATION:
      0–30   → LOW
      30–60  → MODERATE  
      60–80  → HIGH
      80–100 → CRITICAL
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_effective_capacity(self, zone: Zone, call_type: str) -> int:
        """
        Calculate effective capacity from stations.
        Falls back to zone base capacity (not 1) if no stations assigned —
        this was the root cause of false CRITICAL scores.
        """
        stations = [s for s in zone.stations if s.type.value == call_type.lower()]

        if stations:
            return max(1, sum(s.capacity_units for s in stations))

        # FIXED: use zone base capacity as fallback, not 1
        if call_type == "police":
            return max(1, zone.base_capacity_police or 8)
        else:
            return max(1, zone.base_capacity_fire or 5)

    def calculate_risk_score(self,
                             predicted_demand: float,
                             signal_multiplier: float,
                             effective_capacity: int) -> float:
        """
        Normalized risk score 0–100.

        Demand/capacity ratio → scaled so that:
          ratio ≤ 0.5  → score ≤ 30  (LOW)
          ratio ~1.0   → score ~55   (MODERATE/HIGH boundary)
          ratio ≥ 1.5  → score ~80+  (CRITICAL range)

        Signal multiplier amplifies when real-time signals are present.
        """
        if effective_capacity <= 0:
            effective_capacity = 1

        demand_adjusted = predicted_demand * signal_multiplier
        ratio           = demand_adjusted / effective_capacity

        # Sigmoid-like scaling: score = 100 * ratio / (ratio + 0.8)
        # At ratio=0.5 → 38.5, ratio=1.0 → 55.6, ratio=2.0 → 71.4
        score = 100.0 * ratio / (ratio + 0.8)
        return round(min(100.0, max(0.0, score)), 2)

    def run(self):
        zones = self.db.query(Zone).all()

        for zone in zones:
            risk_score = self.db.query(RiskScore).filter(
                RiskScore.zone_id == zone.id
            ).first()

            if not risk_score:
                risk_score = RiskScore(id=f"risk_{zone.id}", zone_id=zone.id)
                self.db.add(risk_score)

            eff_cap_police = self.calculate_effective_capacity(zone, "police")
            eff_cap_fire   = self.calculate_effective_capacity(zone, "fire")

            risk_score.effective_capacity_police = eff_cap_police
            risk_score.effective_capacity_fire   = eff_cap_fire

            police_score = self.calculate_risk_score(
                risk_score.predicted_demand_police or 0,
                risk_score.signal_multiplier or 1.0,
                eff_cap_police,
            )
            fire_score = self.calculate_risk_score(
                risk_score.predicted_demand_fire or 0,
                risk_score.signal_multiplier or 1.0,
                eff_cap_fire,
            )

            risk_score.final_risk_score = max(police_score, fire_score)
            risk_score.updated_at       = datetime.utcnow()

        self.db.commit()