from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.db.database import get_db
from app.auth.middleware import get_current_user, require_role
from app.models.user import UserRole
from app.models.risk import RiskScore
from app.models.zone import Zone
from app.agents.demand_prediction import DemandPredictionAgent
from app.agents.signal_fusion import SignalFusionAgent
from app.agents.risk_scoring import RiskScoringAgent
from app.agents.llm_alerts import generate_zone_alerts
from datetime import datetime, timedelta
import os

router = APIRouter(prefix="/api", tags=["intelligence"])

class ForecastResponse(BaseModel):
    zone_id: str
    zone_name: str
    predicted_police: float
    predicted_fire: float
    timestamp: str

    class Config:
        from_attributes = True


class RiskResponse(BaseModel):
    zone_id: str
    zone_name: str
    final_risk_score: float
    predicted_demand_police: float
    predicted_demand_fire: float
    signal_multiplier: float
    effective_capacity_police: int
    effective_capacity_fire: int

    class Config:
        from_attributes = True


class ResourceRecommendation(BaseModel):
    receiving_zone: str
    donor_zone: str
    units_to_move: int
    unit_type: str
    reasoning: str
    confidence: str
    recommendation_type: str

    class Config:
        from_attributes = True


class NoRecommendation(BaseModel):
    recommendation: None
    message: str

    class Config:
        from_attributes = True


@router.get("/forecast", response_model=List[ForecastResponse])
async def get_forecast(
    current_user: dict = Depends(require_role(
        UserRole.POLICE_ADMIN,
        UserRole.FIRE_ADMIN,
        UserRole.EMERGENCY_MANAGER,
    )),
    db: Session = Depends(get_db),
):
    """Get demand forecast for next 6 hours - Government only"""
    agent = DemandPredictionAgent(db)
    agent.run()
    
    zones = db.query(Zone).all()
    forecasts = []
    
    for zone in zones:
        risk = db.query(RiskScore).filter(RiskScore.zone_id == zone.id).first()
        if risk:
            forecasts.append({
                "zone_id": zone.id,
                "zone_name": zone.name,
                "predicted_police": risk.predicted_demand_police,
                "predicted_fire": risk.predicted_demand_fire,
                "timestamp": risk.updated_at.isoformat(),
            })
    
    return forecasts


@router.get("/risk", response_model=List[RiskResponse])
async def get_risk_scores(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current risk scores for all zones"""
    # Run agents to get latest data
    demand_agent = DemandPredictionAgent(db)
    demand_agent.run()
    
    signal_agent = SignalFusionAgent(db)
    signal_agent.run()
    
    risk_agent = RiskScoringAgent(db)
    risk_agent.run()
    
    risk_scores = db.query(RiskScore).all()
    
    return [
        {
            "zone_id": rs.zone_id,
            "zone_name": rs.zone.name,
            "final_risk_score": rs.final_risk_score,
            "predicted_demand_police": rs.predicted_demand_police,
            "predicted_demand_fire": rs.predicted_demand_fire,
            "signal_multiplier": rs.signal_multiplier,
            "effective_capacity_police": rs.effective_capacity_police,
            "effective_capacity_fire": rs.effective_capacity_fire,
        }
        for rs in risk_scores
    ]


@router.get("/resource-recommendations")
async def get_resource_recommendations(
    current_user: dict = Depends(require_role(
        UserRole.POLICE_ADMIN,
        UserRole.FIRE_ADMIN,
        UserRole.EMERGENCY_MANAGER,
    )),
    db: Session = Depends(get_db),
):
    """Get intelligent resource reallocation recommendations - Government only"""
    from app.models.signal import RealTimeSignal
    from datetime import datetime, timedelta

    # Run agents to get latest data
    demand_agent = DemandPredictionAgent(db)
    demand_agent.run()

    signal_agent = SignalFusionAgent(db)
    signal_agent.run()

    risk_agent = RiskScoringAgent(db)
    risk_agent.run()

    # Query all risk scores with zones
    risk_scores = db.query(RiskScore).join(Zone).all()

    if not risk_scores:
        return {"recommendation": None, "message": "All zones balanced"}

    # Find receiving zone: trend-based trigger (risk > 40 AND signal_multiplier > 1.2)
    receiving_candidates = [
        rs for rs in risk_scores
        if rs.final_risk_score > 40 and rs.signal_multiplier > 1.2
    ]

    if not receiving_candidates:
        return {"recommendation": None, "message": "All zones balanced"}

    # Select receiving zone (highest risk score among candidates)
    receiving_zone = max(receiving_candidates, key=lambda rs: rs.final_risk_score)

    # Count high-severity signals for receiving zone (last 6 hours)
    six_hours_ago = datetime.utcnow() - timedelta(hours=6)
    high_severity_signals = db.query(RealTimeSignal).filter(
        RealTimeSignal.zone_id == receiving_zone.zone_id,
        RealTimeSignal.severity == "high",
        RealTimeSignal.created_at > six_hours_ago
    ).count()

    # Determine recommendation tier and units
    if receiving_zone.final_risk_score > 60:
        # REINFORCE: Risk already high - immediate action needed
        recommendation_type = "reinforce"
        units_to_move = min(2, max(1, int(receiving_zone.effective_capacity_police * 0.15)))
        urgency_text = "Immediate reallocation needed"
        time_frame = "within the next 30 minutes"
    elif receiving_zone.signal_multiplier > 1.4:
        # PRE-POSITION: Risk rising rapidly - proactive action
        recommendation_type = "pre_position"
        units_to_move = min(2, max(1, int(receiving_zone.effective_capacity_police * 0.1)))
        urgency_text = "Move units NOW before spike"
        time_frame = "before 17:00 to avoid reactive response"
    else:
        # MONITOR: Risk elevated but stable - standby mode
        recommendation_type = "monitor"
        units_to_move = 1
        urgency_text = "Keep 1 unit on standby"
        time_frame = "monitor for next 2 hours"

    # Find donor zone: lowest risk where demand < 60% capacity
    donor_candidates = [
        rs for rs in risk_scores
        if rs.predicted_demand_police < rs.effective_capacity_police * 0.6
        and rs.zone_id != receiving_zone.zone_id
    ]

    if not donor_candidates:
        return {"recommendation": None, "message": "All zones balanced"}

    donor_zone = min(donor_candidates, key=lambda rs: rs.final_risk_score)

    # Calculate confidence based on signal strength and risk differential
    risk_diff = receiving_zone.final_risk_score - donor_zone.final_risk_score
    signal_strength = receiving_zone.signal_multiplier
    confidence_score = (risk_diff * 0.4) + (signal_strength * 20) + (high_severity_signals * 5)

    if confidence_score > 50:
        confidence = "high"
    elif confidence_score > 25:
        confidence = "medium"
    else:
        confidence = "low"

    # ── Look up real station names from DB ───────────────────────────
    from app.models.station import Station, StationType

    def get_police_station_name(zone_id: str, fallback: str) -> str:
        station = db.query(Station).filter(
            Station.zone_id == zone_id,
            Station.type == StationType.POLICE,
        ).first()
        return station.name if station else fallback

    receiving_station = get_police_station_name(
        receiving_zone.zone_id,
        f"{receiving_zone.zone.name} Police Station"
    )
    donor_station = get_police_station_name(
        donor_zone.zone_id,
        f"{donor_zone.zone.name} Police Station"
    )

    # Get current day/time context for historical patterns
    now = datetime.utcnow()
    current_hour = now.hour
    current_day = now.weekday()  # 0=Monday, 4=Friday

    # Generate intelligent reasoning based on recommendation type
    if recommendation_type == "reinforce":
        reasoning = (
            f"{receiving_zone.zone.name} shows critical risk level ({receiving_zone.final_risk_score:.0f}) "
            f"with {high_severity_signals} high-severity signals in the last 6 hours. "
            f"Signal multiplier of {receiving_zone.signal_multiplier:.1f}× indicates active incident cluster. "
            f"{urgency_text} — reallocate {units_to_move} unit{'' if units_to_move == 1 else 's'} "
            f"from {donor_station} to {receiving_station} {time_frame}."
        )

    elif recommendation_type == "pre_position":
        time_context = ""
        if current_day == 4 and current_hour >= 16:
            time_context = "Historical Friday evening patterns indicate 40% demand increase likely by 18:00. "
        elif 18 <= current_hour <= 22:
            time_context = "Evening hours typically see 25% demand increase. "

        reasoning = (
            f"{receiving_zone.zone.name} shows elevated signal activity "
            f"({high_severity_signals} high-severity incidents in 6hrs, multiplier {receiving_zone.signal_multiplier:.1f}×). "
            f"{time_context}{urgency_text} — pre-position {units_to_move} unit{'' if units_to_move == 1 else 's'} "
            f"from {donor_station} to {receiving_station} {time_frame}."
        )

    else:  # monitor
        reasoning = (
            f"{receiving_zone.zone.name} shows elevated but stable risk ({receiving_zone.final_risk_score:.0f}) "
            f"with moderate signal activity. "
            f"{urgency_text} at {receiving_station} while maintaining coverage at {donor_station}."
        )

    return {
        "receiving_zone": receiving_zone.zone.name,
        "donor_zone": donor_zone.zone.name,
        "units_to_move": units_to_move,
        "unit_type": "police",
        "reasoning": reasoning,
        "confidence": confidence,
        "recommendation_type": recommendation_type
    }


@router.get("/signals")
async def get_signals(
    current_user: dict = Depends(require_role(
        UserRole.POLICE_ADMIN,
        UserRole.FIRE_ADMIN,
        UserRole.EMERGENCY_MANAGER,
    )),
    db: Session = Depends(get_db),
):
    """Get active real-time signals - Government only"""
    from app.models.signal import RealTimeSignal
    from datetime import datetime
    
    active_signals = db.query(RealTimeSignal).filter(
        RealTimeSignal.expires_at > datetime.utcnow(),
    ).all()
    
    return [
        {
            "id": s.id,
            "zone_id": s.zone_id,
            "zone_name": s.zone.name,
            "signal_type": s.signal_type.value,
            "severity": s.severity,
            "title": s.title,
            "description": s.description,
            "source_link": s.source_link,
            "weight": s.weight,
            "created_at": s.created_at.isoformat(),
        }
        for s in active_signals
    ]


@router.post("/run-agents")
async def run_agents(
    current_user: dict = Depends(require_role(UserRole.EMERGENCY_MANAGER)),
    db: Session = Depends(get_db),
):
    """Manually trigger agent execution"""
    demand_agent = DemandPredictionAgent(db)
    demand_agent.run()
    
    signal_agent = SignalFusionAgent(db)
    signal_agent.run()
    
    risk_agent = RiskScoringAgent(db)
    risk_agent.run()
    
    return {"status": "Agents executed successfully"}


@router.get("/ai-alerts")
async def get_ai_alerts(db: Session = Depends(get_db)):
    from app.models.signal import RealTimeSignal
    risk_scores = db.query(RiskScore).all()
    payload = []
    for rs in risk_scores:
        high_signals = db.query(RealTimeSignal).filter(
            RealTimeSignal.zone_id == rs.zone_id,
            RealTimeSignal.severity == "high",
            RealTimeSignal.expires_at > datetime.utcnow(),
        ).count()
        payload.append({
            "zone_id":                   rs.zone_id,
            "zone_name":                 rs.zone.name if rs.zone else rs.zone_id,
            "final_risk_score":          rs.final_risk_score or 0,
            "predicted_demand_police":   rs.predicted_demand_police or 0,
            "predicted_demand_fire":     rs.predicted_demand_fire or 0,
            "effective_capacity_police": rs.effective_capacity_police or 8,
            "effective_capacity_fire":   rs.effective_capacity_fire or 5,
            "signal_multiplier":         rs.signal_multiplier or 1.0,
            "active_high_signals":       high_signals,
        })
    alerts = generate_zone_alerts(payload)
    return {
        "timestamp":   datetime.utcnow().isoformat(),
        "llm_powered": bool(os.getenv("ANTHROPIC_API_KEY")),
        "alerts":      alerts,
    }