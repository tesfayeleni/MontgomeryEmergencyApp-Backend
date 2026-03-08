from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.auth.middleware import require_role
from app.models.user import UserRole
from app.data_ingestion.brightdata_client import MontgomeryDataClient
from app.data_ingestion.ingestion_service import DataIngestionService
from app.models.call import HistoricalCall, CallType
import logging
import requests
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data-ingestion", tags=["data-ingestion"])


@router.post("/ingest-brightdata")
async def trigger_ingestion(
    current_user: dict = Depends(require_role(UserRole.EMERGENCY_MANAGER)),
    db: Session = Depends(get_db),
):
    """
    Trigger live data ingestion.
    Fetches fire/rescue incidents from Montgomery AL ArcGIS API.
    Police incidents are seeded statically (POC).
    """
    try:
        service = DataIngestionService(db)
        result = service.run_full_ingestion()
        return {
            "status":                    result.get("status"),
            "timestamp":                 result.get("timestamp"),
            "fire_rescue_ingested":      result.get("fire_rescue_ingested", 0),
            # "police_incidents_ingested": result.get("police_incidents_ingested", 0),
            # "stations_fetched":          0,
            "error":                     result.get("error"),
            "debug_info":                result.get("debug_info", []),
        }
    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brightdata-status")
async def status(
    current_user: dict = Depends(require_role(UserRole.EMERGENCY_MANAGER)),
):
    client = MontgomeryDataClient()
    return {
        "status": "configured",
        "api_key_configured": bool(client.api_key),
        "data_sources": {
            "fire_rescue_incidents": "✅ LIVE  — Direct ArcGIS API (Fire_Rescue_All_Incidents/FeatureServer)",
            #"police_incidents":      "📸 STATIC — Seeded from CrimeMapping screenshot. No public API exists.",
            #"news_signals":          "✅ LIVE  — Google RSS via news_agent.py scheduler",
            #"stations":              "✅ SEEDED — 33 real locations from ArcGIS table (one-time)",
            #"911_calls":             "❌ DROPPED — Only aggregate monthly stats, no individual incidents",
            #"flood_zones":           "❌ DROPPED — Out of POC scope",
        },
    }


@router.get("/ingestion-status")
async def ingestion_status(
    current_user: dict = Depends(require_role(UserRole.EMERGENCY_MANAGER)),
    db: Session = Depends(get_db),
):
    try:
        police = db.query(HistoricalCall).filter(HistoricalCall.call_type == CallType.POLICE).count()
        fire   = db.query(HistoricalCall).filter(HistoricalCall.call_type == CallType.FIRE).count()
        return {
            "database_status": "connected",
            "records_in_system": {
                "total":         police + fire,
                "police_calls":  police,
                "fire_calls":    fire,
            },
            "note": "POST /ingest-brightdata to fetch latest fire/rescue incidents",
        }
    except Exception as e:
        return {"database_status": "error", "error": str(e)}