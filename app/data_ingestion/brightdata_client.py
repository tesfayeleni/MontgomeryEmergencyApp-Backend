import requests
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

FIRE_RESCUE_URL = (
    "https://services7.arcgis.com/xNUwUjOJqYE54USz"
    "/arcgis/rest/services/Fire_Rescue_All_Incidents/FeatureServer/0/query"
)


class MontgomeryDataClient:

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BRIGHTDATA_API_KEY", "")
        self.headers = {
            "User-Agent": "MontgomeryEmergencyApp/1.0",
            "Accept": "application/json",
        }

    # ─────────────────────────────────────────────────────────────────
    # DIRECT API — Fire / Rescue Incidents
    # Individual incidents from Montgomery Fire Department.
    # Categories: Fire, Medical, Hazsit, Noemerg, Pubserv, Rescue
    # ─────────────────────────────────────────────────────────────────

    def fetch_fire_rescue_incidents(self, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Fetch individual fire/rescue incidents from Montgomery AL ArcGIS.
        Returns normalised records ready for ingestion_service.
        """
        params = {
            "outFields": "*",
            "where": "1=1",
            "f": "json",
            "resultRecordCount": min(limit, 2000),
        }

        logger.info(f"[DIRECT API] Fire rescue → {FIRE_RESCUE_URL}")
        try:
            resp = requests.get(FIRE_RESCUE_URL, headers=self.headers, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            features = data.get("features", [])

            records = []
            for feature in features:
                attrs = feature.get("attributes", {})
                geom  = feature.get("geometry") or {}
                records.append({
                    "incident_id":   attrs.get("IncidentNumber") or attrs.get("OBJECTID"),
                    "timestamp":     attrs.get("IncidentDate") or attrs.get("Incident_Date"),
                    "call_type":     "fire",
                    "incident_type": attrs.get("IncidentTypeCategory") or attrs.get("Incident_Type"),
                    "unit_name":     attrs.get("UnitName") or attrs.get("Unit_Name"),
                    "location":      attrs.get("Address") or attrs.get("Location"),
                    "district":      attrs.get("District") or attrs.get("Beat"),
                    "latitude":      geom.get("y"),
                    "longitude":     geom.get("x"),
                    "response_time": attrs.get("ResponseTime"),
                })

            logger.info(f"[DIRECT API] Fire rescue incidents: {len(records)}")
            return records

        except Exception as e:
            logger.error(f"[DIRECT API] Fire rescue failed: {e}", exc_info=True)
            return []

    def ingest_all_data(self) -> Dict[str, Any]:
        """Entry point for ingestion_service.py"""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "fire_rescue_incidents": [],
            "debug_info": [],
            "error": None,
        }

        fire = self.fetch_fire_rescue_incidents()
        results["fire_rescue_incidents"] = fire
        results["debug_info"].append(
            f"Fire/rescue: {len(fire)} records via direct ArcGIS API"
        )
        # results["debug_info"].append(
        #     "Police incidents: seeded statically from CrimeMapping screenshot (POC)"
        # )
        results["debug_info"].append(
            "News signals: running live via news_agent.py scheduler"
        )

        return results


# Backwards-compat alias
BrightDataClient = MontgomeryDataClient