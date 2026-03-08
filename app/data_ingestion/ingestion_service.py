from datetime import datetime
from typing import Dict, Any
import uuid
from sqlalchemy.orm import Session
from app.models.call import HistoricalCall, CallType
from app.models.zone import Zone
from app.data_ingestion.brightdata_client import MontgomeryDataClient
import logging

logger = logging.getLogger(__name__)


class DataIngestionService:
    """
    Live data ingestion for Montgomery AL.

    What runs here (continuous, every scheduler tick):
      - Fire/Rescue incidents → direct ArcGIS API → HistoricalCall (FIRE)

    What does NOT run here (handled elsewhere):
      - Police incidents  → seeded statically in seed_db.py (POC)
      - News signals      → news_agent.py scheduler (live, working)
      - Stations          → seeded once in seed_db.py
    """

    def __init__(self, db: Session, api_key: str = None):
        self.db = db
        self.client = MontgomeryDataClient(api_key)
        self.zone_mapping = self._build_zone_mapping()

    def _build_zone_mapping(self) -> Dict[str, str]:
        zones = self.db.query(Zone).all()
        mapping = {}
        for zone in zones:
            mapping[zone.name.lower()] = zone.id
            mapping[zone.name.replace(" ", "").lower()] = zone.id
        mapping.update({
            "downtown":   "zone_downtown",
            "central":    "zone_downtown",
            "east":       "zone_eastside",
            "eastside":   "zone_eastside",
            "east side":  "zone_eastside",
            "west":       "zone_westside",
            "westside":   "zone_westside",
            "west side":  "zone_westside",
            "north":      "zone_northside",
            "northside":  "zone_northside",
            "north side": "zone_northside",
        })
        return mapping

    def map_to_zone(self, location_str=None, latitude=None, longitude=None) -> str:
        if location_str:
            loc = location_str.lower()
            for key, zone_id in self.zone_mapping.items():
                if key in loc:
                    return zone_id
        if latitude is not None and longitude is not None:
            try:
                lat, lon = float(latitude), float(longitude)
                if lon > -86.28:   return "zone_eastside"
                elif lon < -86.38: return "zone_westside"
                elif lat > 32.42:  return "zone_northside"
                else:              return "zone_downtown"
            except (TypeError, ValueError):
                pass
        return "zone_downtown"

    def _parse_timestamp(self, value) -> datetime:
        """Handles Unix ms ints, ISO strings, date strings, numeric strings."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            try:
                ts = value / 1000 if value > 32503680000 else value
                return datetime.utcfromtimestamp(ts)
            except (OSError, OverflowError, ValueError):
                return None
        if isinstance(value, str):
            for fmt in (None, "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%d", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y"):
                try:
                    if fmt is None:
                        return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
                    return datetime.strptime(value.strip(), fmt)
                except (ValueError, TypeError):
                    continue
            try:
                return self._parse_timestamp(float(value))
            except (ValueError, TypeError):
                pass
        return None

    def ingest_fire_rescue(self, records: list) -> int:
        count = 0
        skipped = 0
        try:
            for rec in records:
                try:
                    timestamp = self._parse_timestamp(rec.get("timestamp")) or datetime.utcnow()

                    zone_id = self.map_to_zone(
                        rec.get("location") or rec.get("district"),
                        rec.get("latitude"), rec.get("longitude"),
                    )

                    self.db.add(HistoricalCall(
                        id=str(uuid.uuid4()),
                        zone_id=zone_id,
                        timestamp=timestamp,
                        call_type=CallType.FIRE,
                        response_time=float(rec.get("response_time") or 0) or None,
                        severity=1,
                    ))
                    count += 1
                except Exception as e:
                    logger.warning(f"Record error: {e}")
                    continue

            self.db.commit()
            logger.info(f"Fire/rescue ingested: {count} (skipped {skipped})")

        except Exception as e:
            logger.error(f"Fire/rescue ingestion failed: {e}")
            self.db.rollback()

        return count

    def run_full_ingestion(self) -> Dict[str, Any]:
        logger.info("Starting Montgomery AL ingestion (fire/rescue)...")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "fire_rescue_ingested": 0,
            # "police_incidents_ingested": 0,  # seeded statically, not ingested here
            # "stations_fetched": 0,            # seeded once, not ingested here
            "error": None,
            "debug_info": [],
        }

        try:
            data = self.client.ingest_all_data()
            results["debug_info"] = data.get("debug_info", [])

            if data.get("status") == "error":
                results["status"] = "error"
                results["error"] = data.get("error")
                return results

            results["fire_rescue_ingested"] = self.ingest_fire_rescue(
                data.get("fire_rescue_incidents", [])
            )

            logger.info(f"Ingestion complete — fire/rescue: {results['fire_rescue_ingested']}")

        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            results["debug_info"].append(f"CRITICAL: {e}")

        return results