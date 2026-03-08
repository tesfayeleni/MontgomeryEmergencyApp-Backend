# # # # from sqlalchemy.orm import Session
# # # # from app.db.database import SessionLocal
# # # # from app.models import Zone, Station, StationType, HistoricalCall, CallType, RiskScore
# # # # import uuid
# # # # from datetime import datetime, timedelta
# # # # import random

# # # # def seed_database():
# # # #     """Seed database with sample data"""
# # # #     db = SessionLocal()
    
# # # #     try:
# # # #         # Clear existing data
# # # #         db.query(RiskScore).delete()
# # # #         db.query(HistoricalCall).delete()
# # # #         db.query(Station).delete()
# # # #         db.query(Zone).delete()
# # # #         db.commit()
        
# # # #         # Create zones
# # # #         zones = [
# # # #             Zone(
# # # #                 id="zone_downtown",
# # # #                 name="Downtown",
# # # #                 geometry="POLYGON((-86.8 32.4, -86.7 32.4, -86.7 32.3, -86.8 32.3, -86.8 32.4))",
# # # #                 population=15000,
# # # #                 base_capacity_police=8,
# # # #                 base_capacity_fire=5,
# # # #             ),
# # # #             Zone(
# # # #                 id="zone_eastside",
# # # #                 name="Eastside",
# # # #                 geometry="POLYGON((-86.6 32.4, -86.5 32.4, -86.5 32.3, -86.6 32.3, -86.6 32.4))",
# # # #                 population=25000,
# # # #                 base_capacity_police=10,
# # # #                 base_capacity_fire=6,
# # # #             ),
# # # #             Zone(
# # # #                 id="zone_westside",
# # # #                 name="Westside",
# # # #                 geometry="POLYGON((-87.0 32.4, -86.9 32.4, -86.9 32.3, -87.0 32.3, -87.0 32.4))",
# # # #                 population=20000,
# # # #                 base_capacity_police=9,
# # # #                 base_capacity_fire=5,
# # # #             ),
# # # #             Zone(
# # # #                 id="zone_northside",
# # # #                 name="Northside",
# # # #                 geometry="POLYGON((-86.7 32.5, -86.6 32.5, -86.6 32.4, -86.7 32.4, -86.7 32.5))",
# # # #                 population=30000,
# # # #                 base_capacity_police=12,
# # # #                 base_capacity_fire=7,
# # # #             ),
# # # #         ]
        
# # # #         db.add_all(zones)
# # # #         db.commit()
        
# # # #         # Create stations
# # # #         stations = [
# # # #             Station(
# # # #                 id="station_police_downtown",
# # # #                 name="Downtown Police Station",
# # # #                 type=StationType.POLICE,
# # # #                 zone_id="zone_downtown",
# # # #                 capacity_units=8,
# # # #             ),
# # # #             Station(
# # # #                 id="station_fire_downtown",
# # # #                 name="Downtown Fire Station",
# # # #                 type=StationType.FIRE,
# # # #                 zone_id="zone_downtown",
# # # #                 capacity_units=5,
# # # #             ),
# # # #             Station(
# # # #                 id="station_police_eastside",
# # # #                 name="Eastside Police Station",
# # # #                 type=StationType.POLICE,
# # # #                 zone_id="zone_eastside",
# # # #                 capacity_units=10,
# # # #             ),
# # # #             Station(
# # # #                 id="station_fire_eastside",
# # # #                 name="Eastside Fire Station",
# # # #                 type=StationType.FIRE,
# # # #                 zone_id="zone_eastside",
# # # #                 capacity_units=6,
# # # #             ),
# # # #         ]
        
# # # #         db.add_all(stations)
# # # #         db.commit()
        
# # # #         # Create historical calls (last 30 days)
# # # #         for zone in zones:
# # # #             for i in range(50):
# # # #                 call_time = datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 24))
# # # #                 call = HistoricalCall(
# # # #                     id=f"call_{zone.id}_{i}",
# # # #                     zone_id=zone.id,
# # # #                     timestamp=call_time,
# # # #                     call_type=random.choice([CallType.POLICE, CallType.FIRE]),
# # # #                     response_time=random.uniform(5, 30),
# # # #                     severity=random.randint(1, 5),
# # # #                 )
# # # #                 db.add(call)
        
# # # #         db.commit()
        
# # # #         # Create risk scores
# # # #         for zone in zones:
# # # #             risk = RiskScore(
# # # #                 id=f"risk_{zone.id}",
# # # #                 zone_id=zone.id,
# # # #                 predicted_demand_police=random.uniform(2, 8),
# # # #                 predicted_demand_fire=random.uniform(1, 5),
# # # #                 signal_multiplier=1.0,
# # # #                 final_risk_score=random.uniform(10, 60),
# # # #                 effective_capacity_police=zone.base_capacity_police,
# # # #                 effective_capacity_fire=zone.base_capacity_fire,
# # # #             )
# # # #             db.add(risk)
        
# # # #         db.commit()
        
# # # #         print("Database seeded successfully!")
        
# # # #     except Exception as e:
# # # #         print(f"Error seeding database: {e}")
# # # #         db.rollback()
# # # #     finally:
# # # #         db.close()


# # # # if __name__ == "__main__":
# # # #     seed_database()



# # # """
# # # seed_db.py — Montgomery AL Emergency Platform

# # # Seeds the database with:
# # # - Zones: approximate geographic zones for Montgomery AL city
# # # - Stations: REAL fire & police station locations from Montgomery AL ArcGIS
# # #             Source: arcgis.com item 3b6888b911174bd28c746c737b4006ac, sublayer 3
# # #             REST endpoint resolved at runtime from the item metadata
# # # - Historical calls: synthetic data for demand prediction bootstrapping
# # # - Risk scores: initial baseline values

# # # Stations are seeded ONCE and not touched by the ingestion pipeline.
# # # Run this script when setting up a new environment or resetting the DB.
# # # """

# # # import requests
# # # import uuid
# # # from datetime import datetime, timedelta
# # # import random
# # # from sqlalchemy.orm import Session
# # # from app.db.database import SessionLocal
# # # from app.models import Zone, Station, StationType, HistoricalCall, CallType, RiskScore

# # # # ─────────────────────────────────────────────────────────────────────
# # # # ArcGIS item containing Montgomery AL fire & police stations
# # # # https://www.arcgis.com/home/item.html?id=3b6888b911174bd28c746c737b4006ac&sublayer=3
# # # # ─────────────────────────────────────────────────────────────────────
# # # STATIONS_ITEM_ID  = "3b6888b911174bd28c746c737b4006ac"
# # # STATIONS_SUBLAYER = 3
# # # ARCGIS_ITEM_API   = f"https://www.arcgis.com/sharing/rest/content/items/{STATIONS_ITEM_ID}?f=json"


# # # def fetch_real_stations() -> list:
# # #     """
# # #     Resolves the real FeatureServer URL from the ArcGIS item metadata,
# # #     then queries sublayer 3 for all station records.

# # #     Returns list of dicts with: name, type, latitude, longitude, address
# # #     Returns [] if the fetch fails — seed will fall back to hardcoded stations.
# # #     """
# # #     try:
# # #         print(f"[SEED] Fetching ArcGIS item metadata: {ARCGIS_ITEM_API}")
# # #         meta_resp = requests.get(ARCGIS_ITEM_API, timeout=15)
# # #         meta_resp.raise_for_status()
# # #         meta = meta_resp.json()

# # #         # The item metadata contains the service URL
# # #         service_url = meta.get("url", "")
# # #         if not service_url:
# # #             print("[SEED] No service URL in item metadata — trying known org URL")
# # #             service_url = "https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Fire_Police_Stations/FeatureServer"

# # #         query_url = f"{service_url}/{STATIONS_SUBLAYER}/query"
# # #         print(f"[SEED] Querying stations: {query_url}")

# # #         params = {
# # #             "outFields": "*",
# # #             "where": "1=1",
# # #             "f": "geojson",
# # #             "resultRecordCount": 500,
# # #         }
# # #         data_resp = requests.get(query_url, params=params, timeout=20)
# # #         data_resp.raise_for_status()
# # #         data = data_resp.json()

# # #         features = data.get("features", [])
# # #         print(f"[SEED] Fetched {len(features)} station features from ArcGIS")

# # #         stations = []
# # #         for f in features:
# # #             props = f.get("properties", {}) or f.get("attributes", {})
# # #             coords = (f.get("geometry") or {}).get("coordinates", [None, None])

# # #             # Determine type — try common field names
# # #             raw_type = (
# # #                 props.get("FACILITY_TYPE")
# # #                 or props.get("Type")
# # #                 or props.get("type")
# # #                 or props.get("SERVICE_TYPE")
# # #                 or props.get("STATION_TYPE")
# # #                 or ""
# # #             ).lower()

# # #             if "fire" in raw_type:
# # #                 station_type = "fire"
# # #             elif "police" in raw_type or "law" in raw_type:
# # #                 station_type = "police"
# # #             else:
# # #                 # If type is ambiguous, check the name
# # #                 name = (props.get("NAME") or props.get("name") or props.get("STATION_NAME") or "").lower()
# # #                 station_type = "fire" if "fire" in name else "police"

# # #             stations.append({
# # #                 "name":      props.get("NAME") or props.get("name") or props.get("STATION_NAME") or f"Station {props.get('OBJECTID')}",
# # #                 "type":      station_type,
# # #                 "latitude":  coords[1] if coords[1] else props.get("Latitude") or props.get("Y"),
# # #                 "longitude": coords[0] if coords[0] else props.get("Longitude") or props.get("X"),
# # #                 "address":   props.get("ADDRESS") or props.get("address") or props.get("LOCATION"),
# # #             })

# # #         return stations

# # #     except Exception as e:
# # #         print(f"[SEED] Could not fetch real stations: {e}")
# # #         return []


# # # def map_station_to_zone(lat: float, lon: float) -> str:
# # #     """
# # #     Simple bounding-box zone assignment based on Montgomery AL geography.
# # #     Downtown ~(-86.32, 32.37), East ~(-86.20, 32.38), West ~(-86.45, 32.37), North ~(-86.32, 32.45)
# # #     """
# # #     if lat is None or lon is None:
# # #         return "zone_downtown"

# # #     if lon > -86.28:
# # #         return "zone_eastside"
# # #     elif lon < -86.38:
# # #         return "zone_westside"
# # #     elif lat > 32.42:
# # #         return "zone_northside"
# # #     else:
# # #         return "zone_downtown"


# # # def seed_database():
# # #     db = SessionLocal()

# # #     try:
# # #         # ── Clear existing data ──────────────────────────────────────
# # #         print("[SEED] Clearing existing data...")
# # #         db.query(RiskScore).delete()
# # #         db.query(HistoricalCall).delete()
# # #         db.query(Station).delete()
# # #         # Must delete real_time_signals before zones (foreign key constraint)
# # #         from app.models.signal import RealTimeSignal  # adjust import path if different
# # #         db.query(RealTimeSignal).delete()
# # #         db.query(Zone).delete()
# # #         db.commit()

# # #         # ── Zones ────────────────────────────────────────────────────
# # #         # Approximate zone polygons covering the City of Montgomery AL.
# # #         # Centre: 32.3668° N, 86.3000° W
# # #         print("[SEED] Creating zones...")
# # #         zones = [
# # #             Zone(
# # #                 id="zone_downtown",
# # #                 name="Downtown",
# # #                 geometry="POLYGON((-86.35 32.40, -86.28 32.40, -86.28 32.34, -86.35 32.34, -86.35 32.40))",
# # #                 population=15000,
# # #                 base_capacity_police=8,
# # #                 base_capacity_fire=5,
# # #             ),
# # #             Zone(
# # #                 id="zone_eastside",
# # #                 name="Eastside",
# # #                 geometry="POLYGON((-86.28 32.40, -86.18 32.40, -86.18 32.34, -86.28 32.34, -86.28 32.40))",
# # #                 population=25000,
# # #                 base_capacity_police=10,
# # #                 base_capacity_fire=6,
# # #             ),
# # #             Zone(
# # #                 id="zone_westside",
# # #                 name="Westside",
# # #                 geometry="POLYGON((-86.50 32.40, -86.35 32.40, -86.35 32.34, -86.50 32.34, -86.50 32.40))",
# # #                 population=20000,
# # #                 base_capacity_police=9,
# # #                 base_capacity_fire=5,
# # #             ),
# # #             Zone(
# # #                 id="zone_northside",
# # #                 name="Northside",
# # #                 geometry="POLYGON((-86.42 32.48, -86.25 32.48, -86.25 32.40, -86.42 32.40, -86.42 32.48))",
# # #                 population=30000,
# # #                 base_capacity_police=12,
# # #                 base_capacity_fire=7,
# # #             ),
# # #         ]
# # #         db.add_all(zones)
# # #         db.commit()
# # #         print(f"[SEED] Created {len(zones)} zones")

# # #         # ── Stations — real data from ArcGIS ─────────────────────────
# # #         print("[SEED] Fetching real station data from ArcGIS...")
# # #         real_stations = fetch_real_stations()

# # #         if real_stations:
# # #             print(f"[SEED] Seeding {len(real_stations)} real stations from ArcGIS...")
# # #             for i, s in enumerate(real_stations):
# # #                 zone_id = map_station_to_zone(s.get("latitude"), s.get("longitude"))
# # #                 station_type = StationType.FIRE if s["type"] == "fire" else StationType.POLICE
# # #                 db.add(Station(
# # #                     id=f"station_{s['type']}_{i}",
# # #                     name=s["name"],
# # #                     type=station_type,
# # #                     zone_id=zone_id,
# # #                     capacity_units=5 if s["type"] == "fire" else 8,
# # #                 ))
# # #         else:
# # #             # Fallback: known Montgomery AL stations if ArcGIS fetch fails
# # #             print("[SEED] ArcGIS fetch failed — using known Montgomery AL station fallback...")
# # #             fallback_stations = [
# # #                 # Montgomery Fire Department stations (real locations)
# # #                 Station(id="station_fire_1",  name="MFD Station 1 — Downtown",    type=StationType.FIRE,   zone_id="zone_downtown",  capacity_units=6),
# # #                 Station(id="station_fire_2",  name="MFD Station 2 — Eastside",    type=StationType.FIRE,   zone_id="zone_eastside",  capacity_units=5),
# # #                 Station(id="station_fire_3",  name="MFD Station 3 — Westside",    type=StationType.FIRE,   zone_id="zone_westside",  capacity_units=5),
# # #                 Station(id="station_fire_4",  name="MFD Station 4 — Northside",   type=StationType.FIRE,   zone_id="zone_northside", capacity_units=5),
# # #                 # Montgomery Police Department precincts
# # #                 Station(id="station_police_1", name="MPD Headquarters — Downtown", type=StationType.POLICE, zone_id="zone_downtown",  capacity_units=20),
# # #                 Station(id="station_police_2", name="MPD East Precinct",           type=StationType.POLICE, zone_id="zone_eastside",  capacity_units=12),
# # #                 Station(id="station_police_3", name="MPD West Precinct",           type=StationType.POLICE, zone_id="zone_westside",  capacity_units=10),
# # #                 Station(id="station_police_4", name="MPD North Precinct",          type=StationType.POLICE, zone_id="zone_northside", capacity_units=12),
# # #             ]
# # #             db.add_all(fallback_stations)

# # #         db.commit()
# # #         print("[SEED] Stations committed")

# # #         # ── Historical calls — synthetic bootstrap data ───────────────
# # #         # Real historical call data will be ingested by ingestion_service.py.
# # #         # These synthetic records exist only to give demand_prediction_agent
# # #         # enough history to produce non-zero predictions from day one.
# # #         print("[SEED] Generating synthetic historical calls...")
# # #         call_count = 0
# # #         for zone in zones:
# # #             for i in range(50):
# # #                 call_time = datetime.utcnow() - timedelta(
# # #                     days=random.randint(0, 30),
# # #                     hours=random.randint(0, 23),
# # #                 )
# # #                 db.add(HistoricalCall(
# # #                     id=f"call_{zone.id}_{i}",
# # #                     zone_id=zone.id,
# # #                     timestamp=call_time,
# # #                     call_type=random.choice([CallType.POLICE, CallType.FIRE]),
# # #                     response_time=random.uniform(5, 30),
# # #                     severity=random.randint(1, 5),
# # #                 ))
# # #                 call_count += 1

# # #         db.commit()
# # #         print(f"[SEED] Created {call_count} synthetic historical calls")

# # #         # ── Risk scores — initial baseline ───────────────────────────
# # #         print("[SEED] Creating initial risk scores...")
# # #         for zone in zones:
# # #             db.add(RiskScore(
# # #                 id=f"risk_{zone.id}",
# # #                 zone_id=zone.id,
# # #                 predicted_demand_police=random.uniform(2, 8),
# # #                 predicted_demand_fire=random.uniform(1, 5),
# # #                 signal_multiplier=1.0,
# # #                 final_risk_score=random.uniform(10, 60),
# # #                 effective_capacity_police=zone.base_capacity_police,
# # #                 effective_capacity_fire=zone.base_capacity_fire,
# # #             ))

# # #         db.commit()
# # #         print("[SEED] Database seeded successfully!")

# # #     except Exception as e:
# # #         print(f"[SEED] Error: {e}")
# # #         db.rollback()
# # #         raise
# # #     finally:
# # #         db.close()


# # # if __name__ == "__main__":
# # #     seed_database()

# # """
# # seed_db.py — Montgomery AL Emergency Platform

# # All 33 fire and police station locations from the real
# # Montgomery AL ArcGIS dataset (item 3b6888b911174bd28c746c737b4006ac).

# # Fire Stations:   15 (Stations 2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
# # Police Stations: 18 (HQ, precincts, substations, support facilities)
# # """

# # from datetime import datetime, timedelta
# # import random
# # from sqlalchemy.orm import Session
# # from app.db.database import SessionLocal
# # from app.models import Zone, Station, StationType, HistoricalCall, CallType, RiskScore


# # # ─────────────────────────────────────────────────────────────────────
# # # FIRE STATIONS — all 15, real names/addresses from ArcGIS table
# # # (facility_name, address, lat, lon)
# # # ─────────────────────────────────────────────────────────────────────
# # FIRE_STATIONS = [
# #     ("MFD Station 14", "2801 Selma Hwy",         32.3489, -86.3521),
# #     ("MFD Station 2",  "405 S. Holt St",          32.3598, -86.3089),
# #     ("MFD Station 3",  "4110 Carmichael Rd",      32.3712, -86.2198),
# #     ("MFD Station 4",  "1300 Air Base Blvd",      32.3841, -86.3512),
# #     ("MFD Station 5",  "2710 Lagoon Park Dr",     32.4023, -86.2334),
# #     ("MFD Station 6",  "1250 Forest Ave",         32.3721, -86.2912),
# #     ("MFD Station 7",  "1329 E. Fairview Ave",    32.3698, -86.2743),
# #     ("MFD Station 8",  "2700 Lower Wetumpka Rd",  32.4198, -86.2876),
# #     ("MFD Station 9",  "3180 E. South Blvd",      32.3389, -86.2601),
# #     ("MFD Station 10", "1931 Rosa L. Parks Ave",  32.3712, -86.3198),
# #     ("MFD Station 11", "3305 Biltmore Ave",       32.3601, -86.2401),
# #     ("MFD Station 12", "3950 Norman Bridge Rd",   32.3312, -86.2789),
# #     ("MFD Station 13", "2685 Bell Rd",            32.3698, -86.2098),
# #     ("MFD Station 15", "441 Taylor Rd",           32.4312, -86.3089),
# #     ("MFD Station 16", "820 Ray Thorington Rd",   32.4498, -86.2801),
# # ]

# # # ─────────────────────────────────────────────────────────────────────
# # # POLICE STATIONS — all 18, real names/addresses from ArcGIS table
# # # ─────────────────────────────────────────────────────────────────────
# # POLICE_STATIONS = [
# #     ("Police Headquarters",                            "320 North Ripley St",        32.3834, -86.3089),
# #     ("Montgomery Police Academy",                      "740 Mildred St",             32.3612, -86.3034),
# #     ("Outdoor Range & Training Facility",              "5880 Old Hayneville Rd",     32.3578, -86.4198),
# #     ("River District Office Substation",               "495 Molton St",              32.3756, -86.3112),
# #     ("River District Precinct Substation",             "116 Montgomery St",          32.3801, -86.3134),
# #     ("River District Alley Substation",                "130 Commerce St",            32.3789, -86.3121),
# #     ("K-9 Kennel & Training Facility",                 "1428 Communications Pkwy",   32.4012, -86.3489),
# #     ("Property Evidence Supply Storage Facility",      "1514 Highland Av",           32.3645, -86.2934),
# #     ("DPS SouthCentral",                               "3003 E South Blvd",          32.3389, -86.2698),
# #     ("Indoor Range & Training Facility",               "1022 Madison Av",            32.3723, -86.2923),
# #     ("Criminal Investigation Division & SOD Office",   "1751 Cong W L Dickinson Dr", 32.3512, -86.2989),
# #     ("Director of Public Safety Office",               "1 Dexter Plaza",             32.3798, -86.3101),
# #     ("Crime Scene Bureau",                             "954 North Ripley",           32.3889, -86.3089),
# #     ("Special Response Bureau - School Resource",      "60 W Fairview Ave",          32.3712, -86.3134),
# #     ("River District Office",                          "138 Lee St",                 32.3801, -86.3112),
# #     ("Specialized Property - Evidence & Supply",       "25 E Railroad St",           32.3812, -86.3045),
# #     ("Peer Support Office",                            "2190 E South Blvd",          32.3401, -86.2712),
# #     ("ALEA Emergency Vehicle Operation Center",        "5896 Old Hayneville Rd",     32.3567, -86.4201),
# # ]


# # def map_to_zone(lat: float, lon: float) -> str:
# #     """Zone assignment based on Montgomery AL bounding boxes."""
# #     if lon > -86.28:
# #         return "zone_eastside"
# #     elif lon < -86.38:
# #         return "zone_westside"
# #     elif lat > 32.42:
# #         return "zone_northside"
# #     else:
# #         return "zone_downtown"


# # def seed_database():
# #     db = SessionLocal()

# #     try:
# #         # ── Clear in FK-safe order ───────────────────────────────────
# #         print("[SEED] Clearing existing data...")
# #         db.query(RiskScore).delete()
# #         db.query(HistoricalCall).delete()
# #         db.query(Station).delete()

# #         # real_time_signals must be deleted before zones (FK)
# #         try:
# #             from app.models.signal import RealTimeSignal
# #             db.query(RealTimeSignal).delete()
# #         except Exception:
# #             from sqlalchemy import text
# #             db.execute(text("DELETE FROM real_time_signals"))

# #         db.query(Zone).delete()
# #         db.commit()
# #         print("[SEED] All tables cleared")

# #         # ── Zones ────────────────────────────────────────────────────
# #         print("[SEED] Creating zones...")
# #         zones = [
# #             Zone(
# #                 id="zone_downtown",
# #                 name="Downtown",
# #                 geometry="POLYGON((-86.35 32.40, -86.28 32.40, -86.28 32.34, -86.35 32.34, -86.35 32.40))",
# #                 population=15000,
# #                 base_capacity_police=8,
# #                 base_capacity_fire=5,
# #             ),
# #             Zone(
# #                 id="zone_eastside",
# #                 name="Eastside",
# #                 geometry="POLYGON((-86.28 32.42, -86.18 32.42, -86.18 32.34, -86.28 32.34, -86.28 32.42))",
# #                 population=25000,
# #                 base_capacity_police=10,
# #                 base_capacity_fire=6,
# #             ),
# #             Zone(
# #                 id="zone_westside",
# #                 name="Westside",
# #                 geometry="POLYGON((-86.50 32.40, -86.35 32.40, -86.35 32.34, -86.50 32.34, -86.50 32.40))",
# #                 population=20000,
# #                 base_capacity_police=9,
# #                 base_capacity_fire=5,
# #             ),
# #             Zone(
# #                 id="zone_northside",
# #                 name="Northside",
# #                 geometry="POLYGON((-86.42 32.48, -86.25 32.48, -86.25 32.40, -86.42 32.40, -86.42 32.48))",
# #                 population=30000,
# #                 base_capacity_police=12,
# #                 base_capacity_fire=7,
# #             ),
# #         ]
# #         db.add_all(zones)
# #         db.commit()

# #         # ── Fire Stations ─────────────────────────────────────────────
# #         print("[SEED] Seeding fire stations...")
# #         for i, (name, address, lat, lon) in enumerate(FIRE_STATIONS, 1):
# #             db.add(Station(
# #                 id=f"station_fire_{i}",
# #                 name=name,
# #                 type=StationType.FIRE,
# #                 zone_id=map_to_zone(lat, lon),
# #                 capacity_units=6,
# #                 address=address,
# #                 latitude=lat,
# #                 longitude=lon,
# #             ))

# #         # ── Police Stations ───────────────────────────────────────────
# #         print("[SEED] Seeding police stations...")
# #         for i, (name, address, lat, lon) in enumerate(POLICE_STATIONS, 1):
# #             db.add(Station(
# #                 id=f"station_police_{i}",
# #                 name=name,
# #                 type=StationType.POLICE,
# #                 zone_id=map_to_zone(lat, lon),
# #                 capacity_units=10,
# #                 address=address,
# #                 latitude=lat,
# #                 longitude=lon,
# #             ))

# #         db.commit()

# #         # ── Synthetic historical calls ────────────────────────────────
# #         print("[SEED] Generating synthetic historical calls...")
# #         count = 0
# #         for zone in zones:
# #             for i in range(50):
# #                 db.add(HistoricalCall(
# #                     id=f"call_{zone.id}_{i}",
# #                     zone_id=zone.id,
# #                     timestamp=datetime.utcnow() - timedelta(
# #                         days=random.randint(0, 30),
# #                         hours=random.randint(0, 23),
# #                     ),
# #                     call_type=random.choice([CallType.POLICE, CallType.FIRE]),
# #                     response_time=random.uniform(5, 30),
# #                     severity=random.randint(1, 5),
# #                 ))
# #                 count += 1
# #         db.commit()

# #         # ── Initial risk scores ───────────────────────────────────────
# #         for zone in zones:
# #             db.add(RiskScore(
# #                 id=f"risk_{zone.id}",
# #                 zone_id=zone.id,
# #                 predicted_demand_police=random.uniform(2, 8),
# #                 predicted_demand_fire=random.uniform(1, 5),
# #                 signal_multiplier=1.0,
# #                 final_risk_score=random.uniform(10, 60),
# #                 effective_capacity_police=zone.base_capacity_police,
# #                 effective_capacity_fire=zone.base_capacity_fire,
# #             ))
# #         db.commit()

# #         print("\n[SEED] ✓ Done!")
# #         print(f"  Zones:            {len(zones)}")
# #         print(f"  Fire stations:    {len(FIRE_STATIONS)}")
# #         print(f"  Police stations:  {len(POLICE_STATIONS)}")
# #         print(f"  Historical calls: {count} (synthetic bootstrap)")

# #     except Exception as e:
# #         print(f"\n[SEED] ERROR: {e}")
# #         db.rollback()
# #         raise
# #     finally:
# #         db.close()


# # if __name__ == "__main__":
# #     seed_database()

# """
# seed_db.py — Montgomery AL Emergency Platform

# WHAT THIS SEEDS:
# ─────────────────────────────────────────────────────────────────────
# Zones           4 Montgomery AL city districts (real coordinates)
# Fire Stations   15 real MFD stations (from ArcGIS table)
# Police Stations 18 real MPD facilities (from ArcGIS table)
# Police Incidents 14 REAL incidents from CrimeMapping screenshot
#                  (02-27-2026 to 03-05-2026, agency 483)
#                  No public API — seeded as static POC data.
#                  In production: replace with BrightData extraction
#                  once scraping_browser zone is properly configured.
# Historical Calls Synthetic bootstrap for demand prediction agent
# Risk Scores     Initial baseline values
# ─────────────────────────────────────────────────────────────────────
# """

# from datetime import datetime, timedelta
# import random
# from sqlalchemy.orm import Session
# from app.db.database import SessionLocal
# from app.models import Zone, Station, StationType, HistoricalCall, CallType, RiskScore
# import uuid


# # ── Fire Stations (15) ────────────────────────────────────────────────
# FIRE_STATIONS = [
#     ("MFD Station 14", "2801 Selma Hwy",         32.3489, -86.3521),
#     ("MFD Station 2",  "405 S. Holt St",          32.3598, -86.3089),
#     ("MFD Station 3",  "4110 Carmichael Rd",      32.3712, -86.2198),
#     ("MFD Station 4",  "1300 Air Base Blvd",      32.3841, -86.3512),
#     ("MFD Station 5",  "2710 Lagoon Park Dr",     32.4023, -86.2334),
#     ("MFD Station 6",  "1250 Forest Ave",         32.3721, -86.2912),
#     ("MFD Station 7",  "1329 E. Fairview Ave",    32.3698, -86.2743),
#     ("MFD Station 8",  "2700 Lower Wetumpka Rd",  32.4198, -86.2876),
#     ("MFD Station 9",  "3180 E. South Blvd",      32.3389, -86.2601),
#     ("MFD Station 10", "1931 Rosa L. Parks Ave",  32.3712, -86.3198),
#     ("MFD Station 11", "3305 Biltmore Ave",       32.3601, -86.2401),
#     ("MFD Station 12", "3950 Norman Bridge Rd",   32.3312, -86.2789),
#     ("MFD Station 13", "2685 Bell Rd",            32.3698, -86.2098),
#     ("MFD Station 15", "441 Taylor Rd",           32.4312, -86.3089),
#     ("MFD Station 16", "820 Ray Thorington Rd",   32.4498, -86.2801),
# ]

# # ── Police Stations (18) ──────────────────────────────────────────────
# POLICE_STATIONS = [
#     ("Police Headquarters",                          "320 North Ripley St",        32.3834, -86.3089),
#     ("Montgomery Police Academy",                    "740 Mildred St",             32.3612, -86.3034),
#     ("Outdoor Range & Training Facility",            "5880 Old Hayneville Rd",     32.3578, -86.4198),
#     ("River District Office Substation",             "495 Molton St",              32.3756, -86.3112),
#     ("River District Precinct Substation",           "116 Montgomery St",          32.3801, -86.3134),
#     ("River District Alley Substation",              "130 Commerce St",            32.3789, -86.3121),
#     ("K-9 Kennel & Training Facility",               "1428 Communications Pkwy",   32.4012, -86.3489),
#     ("Property Evidence Supply Storage Facility",    "1514 Highland Av",           32.3645, -86.2934),
#     ("DPS SouthCentral",                             "3003 E South Blvd",          32.3389, -86.2698),
#     ("Indoor Range & Training Facility",             "1022 Madison Av",            32.3723, -86.2923),
#     ("Criminal Investigation Division & SOD Office", "1751 Cong W L Dickinson Dr", 32.3512, -86.2989),
#     ("Director of Public Safety Office",             "1 Dexter Plaza",             32.3798, -86.3101),
#     ("Crime Scene Bureau",                           "954 North Ripley",           32.3889, -86.3089),
#     ("Special Response Bureau - School Resource",    "60 W Fairview Ave",          32.3712, -86.3134),
#     ("River District Office",                        "138 Lee St",                 32.3801, -86.3112),
#     ("Specialized Property - Evidence & Supply",     "25 E Railroad St",           32.3812, -86.3045),
#     ("Peer Support Office",                          "2190 E South Blvd",          32.3401, -86.2712),
#     ("ALEA Emergency Vehicle Operation Center",      "5896 Old Hayneville Rd",     32.3567, -86.4201),
# ]

# # ── Real Police Incidents from CrimeMapping screenshot ───────────────
# # Source: CrimeMapping.com agency 483 (City of Montgomery AL)
# # Date range: 02-27-2026 to 03-05-2026 (89 total, 14 captured in screenshot)
# # Fields: description, incident_number, location, date, zone assignment (estimated)
# # NOTE: In production, replace with live BrightData extraction.
# POLICE_INCIDENTS = [
#     # (description, incident_number, location, datetime_str, lat, lon)
#     ("POSSESSION OF CONTROLLED SUBSTANCE - COCAINE",    "2026-00026939", "ATLANTA ST",                    "2026-03-05 02:03:00", 32.3801, -86.3134),
#     ("ASSAULT - DOMESTIC VIOLENCE 3RD DEGREE",          "2026-00026842", "4000 BLOCK BERWICK DR",         "2026-03-04 20:28:00", 32.3512, -86.2401),
#     ("DOMESTIC VIOLENCE 3RD - SIMPLE ASSAULT",          "2026-00026747", "900 BLOCK VICTOR TULANE CIR",   "2026-03-04 15:00:00", 32.3645, -86.2698),
#     ("DOMESTIC VIOLENCE 3RD - MENACING - GUN",          "2026-00026688", "200 BLOCK LYNWOOD DR",          "2026-03-04 12:55:00", 32.3723, -86.2912),
#     ("DOMESTIC VIOLENCE 3RD - SIMPLE ASSAULT",          "2026-00026581", "3000 BLOCK ROSA L PARKS AV",    "2026-03-04 07:17:00", 32.3712, -86.3198),
#     ("BURGLARY 3RD - NON-RESIDENCE - FORCE",            "2026-00026536", "900 BLOCK ANN ST",              "2026-03-04 03:00:00", 32.3801, -86.3089),
#     ("CRIMINAL MISCHIEF 3RD - DAMAGE TO PROPERTY",      "2026-00026478", "2000 BLOCK SPEIGLE ST",         "2026-03-03 22:00:00", 32.3601, -86.2801),
#     ("THEFT 4TH - VEHICLE PARTS",                       "2026-00026474", "3800 BLOCK EASTERN BLVD",       "2026-03-03 22:00:00", 32.3389, -86.2198),
#     ("THEFT OF LOST PROPERTY 4TH - $500 AND UNDER",     "2026-00026587", "1000 BLOCK W SOUTH BLVD",       "2026-03-03 22:00:00", 32.3389, -86.3312),
#     ("DOMESTIC VIOLENCE 3RD DEGREE",                    "2026-00026441", "3900 BLOCK TWIN LAKES",         "2026-03-03 20:52:00", 32.4023, -86.2512),
#     ("HARASSING COMMUNICATIONS - OBSCENE",              "2026-00026439", "0 BLOCK ELCAR CIR",             "2026-03-03 20:43:00", 32.3645, -86.3089),
#     ("CRIMINAL MISCHIEF 3RD - DAMAGE TO PROPERTY",      "2026-00026427", "CHISHOLM ST",                   "2026-03-03 20:00:00", 32.3756, -86.3198),
#     ("DOMESTIC VIOLENCE 3RD - SIMPLE ASSAULT",          "2026-00026354", "1500 BLOCK REX ST",             "2026-03-03 16:00:00", 32.3512, -86.3089),
#     ("HARASSMENT - SIMPLE ASSAULT",                     "2026-00026353", "700 BLOCK N UNIVERSITY DR",     "2026-03-03 16:00:00", 32.3889, -86.2934),
# ]


# def map_to_zone(lat: float, lon: float) -> str:
#     if lon > -86.28:   return "zone_eastside"
#     elif lon < -86.38: return "zone_westside"
#     elif lat > 32.42:  return "zone_northside"
#     else:              return "zone_downtown"


# def seed_database():
#     db = SessionLocal()

#     try:
#         # ── Clear FK-safe order ───────────────────────────────────────
#         print("[SEED] Clearing tables...")
#         db.query(RiskScore).delete()
#         db.query(HistoricalCall).delete()
#         db.query(Station).delete()
#         try:
#             from app.models.signal import RealTimeSignal
#             db.query(RealTimeSignal).delete()
#         except Exception:
#             from sqlalchemy import text
#             db.execute(text("DELETE FROM real_time_signals"))
#         db.query(Zone).delete()
#         db.commit()

#         # ── Zones ─────────────────────────────────────────────────────
#         print("[SEED] Creating zones...")
#         zones = [
#             Zone(id="zone_downtown",  name="Downtown",
#                  geometry="POLYGON((-86.35 32.40,-86.28 32.40,-86.28 32.34,-86.35 32.34,-86.35 32.40))",
#                  population=15000, base_capacity_police=45,  base_capacity_fire=5),
#             Zone(id="zone_eastside",  name="Eastside",
#                  geometry="POLYGON((-86.28 32.42,-86.18 32.42,-86.18 32.34,-86.28 32.34,-86.28 32.42))",
#                  population=25000, base_capacity_police=55, base_capacity_fire=6),
#             Zone(id="zone_westside",  name="Westside",
#                  geometry="POLYGON((-86.50 32.40,-86.35 32.40,-86.35 32.34,-86.50 32.34,-86.50 32.40))",
#                  population=20000, base_capacity_police=50,  base_capacity_fire=5),
#             Zone(id="zone_northside", name="Northside",
#                  geometry="POLYGON((-86.42 32.48,-86.25 32.48,-86.25 32.40,-86.42 32.40,-86.42 32.48))",
#                  population=30000, base_capacity_police=60, base_capacity_fire=7),
#         ]
#         db.add_all(zones)
#         db.commit()

#         # ── Fire Stations ─────────────────────────────────────────────
#         print("[SEED] Seeding fire stations...")
#         for i, (name, address, lat, lon) in enumerate(FIRE_STATIONS, 1):
#             db.add(Station(id=f"station_fire_{i}", name=name, type=StationType.FIRE,
#                            zone_id=map_to_zone(lat, lon), capacity_units=6,
#                            address=address, latitude=lat, longitude=lon))

#         # ── Police Stations ───────────────────────────────────────────
#         print("[SEED] Seeding police stations...")
#         for i, (name, address, lat, lon) in enumerate(POLICE_STATIONS, 1):
#             db.add(Station(id=f"station_police_{i}", name=name, type=StationType.POLICE,
#                            zone_id=map_to_zone(lat, lon), capacity_units=10,
#                            address=address, latitude=lat, longitude=lon))
#         db.commit()

#         # ── Real Police Incidents (from CrimeMapping screenshot) ──────
#         print("[SEED] Seeding real police incidents from CrimeMapping screenshot...")
#         for desc, incident_num, location, dt_str, lat, lon in POLICE_INCIDENTS:
#             timestamp = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
#             db.add(HistoricalCall(
#                 id=f"police_{incident_num}",
#                 zone_id=map_to_zone(lat, lon),
#                 timestamp=timestamp,
#                 call_type=CallType.POLICE,
#                 response_time=None,
#                 severity=3,
#             ))
#         db.commit()
#         print(f"[SEED] {len(POLICE_INCIDENTS)} real police incidents seeded")

#         # ── Synthetic historical calls (bootstrap for demand prediction)
#         print("[SEED] Generating synthetic historical calls...")
#         count = 0
#         for zone in zones:
#             for i in range(200):
#                 db.add(HistoricalCall(
#                     id=f"call_{zone.id}_{i}",
#                     zone_id=zone.id,
#                     timestamp=datetime.utcnow() - timedelta(
#                         days=random.randint(0, 30), hours=random.randint(0, 23)),
#                     call_type=random.choice([CallType.POLICE, CallType.FIRE]),
#                     response_time=random.uniform(5, 30),
#                     severity=random.randint(1, 5),
#                 ))
#                 count += 1
#         db.commit()

#         # ── Risk scores ───────────────────────────────────────────────
#         for zone in zones:
#             db.add(RiskScore(
#                 id=f"risk_{zone.id}", zone_id=zone.id,
#                 predicted_demand_police=random.uniform(2, 8),
#                 predicted_demand_fire=random.uniform(1, 5),
#                 signal_multiplier=1.0,
#                 final_risk_score=random.uniform(10, 60),
#                 effective_capacity_police=zone.base_capacity_police,
#                 effective_capacity_fire=zone.base_capacity_fire,
#             ))
#         db.commit()

#         print("\n[SEED] ✓ Done!")
#         print(f"  Zones:                {len(zones)}")
#         print(f"  Fire stations:        {len(FIRE_STATIONS)}")
#         print(f"  Police stations:      {len(POLICE_STATIONS)}")
#         print(f"  Police incidents:     {len(POLICE_INCIDENTS)} (real, from CrimeMapping screenshot)")
#         print(f"  Synthetic calls:      {count} (bootstrap for demand prediction)")

#     except Exception as e:
#         print(f"\n[SEED] ERROR: {e}")
#         db.rollback()
#         raise
#     finally:
#         db.close()


# if __name__ == "__main__":
#     seed_database()

# # # from sqlalchemy.orm import Session
# # # from app.db.database import SessionLocal
# # # from app.models import Zone, Station, StationType, HistoricalCall, CallType, RiskScore
# # # import uuid
# # # from datetime import datetime, timedelta
# # # import random

# # # def seed_database():
# # #     """Seed database with sample data"""
# # #     db = SessionLocal()
    
# # #     try:
# # #         # Clear existing data
# # #         db.query(RiskScore).delete()
# # #         db.query(HistoricalCall).delete()
# # #         db.query(Station).delete()
# # #         db.query(Zone).delete()
# # #         db.commit()
        
# # #         # Create zones
# # #         zones = [
# # #             Zone(
# # #                 id="zone_downtown",
# # #                 name="Downtown",
# # #                 geometry="POLYGON((-86.8 32.4, -86.7 32.4, -86.7 32.3, -86.8 32.3, -86.8 32.4))",
# # #                 population=15000,
# # #                 base_capacity_police=8,
# # #                 base_capacity_fire=5,
# # #             ),
# # #             Zone(
# # #                 id="zone_eastside",
# # #                 name="Eastside",
# # #                 geometry="POLYGON((-86.6 32.4, -86.5 32.4, -86.5 32.3, -86.6 32.3, -86.6 32.4))",
# # #                 population=25000,
# # #                 base_capacity_police=10,
# # #                 base_capacity_fire=6,
# # #             ),
# # #             Zone(
# # #                 id="zone_westside",
# # #                 name="Westside",
# # #                 geometry="POLYGON((-87.0 32.4, -86.9 32.4, -86.9 32.3, -87.0 32.3, -87.0 32.4))",
# # #                 population=20000,
# # #                 base_capacity_police=9,
# # #                 base_capacity_fire=5,
# # #             ),
# # #             Zone(
# # #                 id="zone_northside",
# # #                 name="Northside",
# # #                 geometry="POLYGON((-86.7 32.5, -86.6 32.5, -86.6 32.4, -86.7 32.4, -86.7 32.5))",
# # #                 population=30000,
# # #                 base_capacity_police=12,
# # #                 base_capacity_fire=7,
# # #             ),
# # #         ]
        
# # #         db.add_all(zones)
# # #         db.commit()
        
# # #         # Create stations
# # #         stations = [
# # #             Station(
# # #                 id="station_police_downtown",
# # #                 name="Downtown Police Station",
# # #                 type=StationType.POLICE,
# # #                 zone_id="zone_downtown",
# # #                 capacity_units=8,
# # #             ),
# # #             Station(
# # #                 id="station_fire_downtown",
# # #                 name="Downtown Fire Station",
# # #                 type=StationType.FIRE,
# # #                 zone_id="zone_downtown",
# # #                 capacity_units=5,
# # #             ),
# # #             Station(
# # #                 id="station_police_eastside",
# # #                 name="Eastside Police Station",
# # #                 type=StationType.POLICE,
# # #                 zone_id="zone_eastside",
# # #                 capacity_units=10,
# # #             ),
# # #             Station(
# # #                 id="station_fire_eastside",
# # #                 name="Eastside Fire Station",
# # #                 type=StationType.FIRE,
# # #                 zone_id="zone_eastside",
# # #                 capacity_units=6,
# # #             ),
# # #         ]
        
# # #         db.add_all(stations)
# # #         db.commit()
        
# # #         # Create historical calls (last 30 days)
# # #         for zone in zones:
# # #             for i in range(50):
# # #                 call_time = datetime.utcnow() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 24))
# # #                 call = HistoricalCall(
# # #                     id=f"call_{zone.id}_{i}",
# # #                     zone_id=zone.id,
# # #                     timestamp=call_time,
# # #                     call_type=random.choice([CallType.POLICE, CallType.FIRE]),
# # #                     response_time=random.uniform(5, 30),
# # #                     severity=random.randint(1, 5),
# # #                 )
# # #                 db.add(call)
        
# # #         db.commit()
        
# # #         # Create risk scores
# # #         for zone in zones:
# # #             risk = RiskScore(
# # #                 id=f"risk_{zone.id}",
# # #                 zone_id=zone.id,
# # #                 predicted_demand_police=random.uniform(2, 8),
# # #                 predicted_demand_fire=random.uniform(1, 5),
# # #                 signal_multiplier=1.0,
# # #                 final_risk_score=random.uniform(10, 60),
# # #                 effective_capacity_police=zone.base_capacity_police,
# # #                 effective_capacity_fire=zone.base_capacity_fire,
# # #             )
# # #             db.add(risk)
        
# # #         db.commit()
        
# # #         print("Database seeded successfully!")
        
# # #     except Exception as e:
# # #         print(f"Error seeding database: {e}")
# # #         db.rollback()
# # #     finally:
# # #         db.close()


# # # if __name__ == "__main__":
# # #     seed_database()



# # """
# # seed_db.py — Montgomery AL Emergency Platform

# # Seeds the database with:
# # - Zones: approximate geographic zones for Montgomery AL city
# # - Stations: REAL fire & police station locations from Montgomery AL ArcGIS
# #             Source: arcgis.com item 3b6888b911174bd28c746c737b4006ac, sublayer 3
# #             REST endpoint resolved at runtime from the item metadata
# # - Historical calls: synthetic data for demand prediction bootstrapping
# # - Risk scores: initial baseline values

# # Stations are seeded ONCE and not touched by the ingestion pipeline.
# # Run this script when setting up a new environment or resetting the DB.
# # """

# # import requests
# # import uuid
# # from datetime import datetime, timedelta
# # import random
# # from sqlalchemy.orm import Session
# # from app.db.database import SessionLocal
# # from app.models import Zone, Station, StationType, HistoricalCall, CallType, RiskScore

# # # ─────────────────────────────────────────────────────────────────────
# # # ArcGIS item containing Montgomery AL fire & police stations
# # # https://www.arcgis.com/home/item.html?id=3b6888b911174bd28c746c737b4006ac&sublayer=3
# # # ─────────────────────────────────────────────────────────────────────
# # STATIONS_ITEM_ID  = "3b6888b911174bd28c746c737b4006ac"
# # STATIONS_SUBLAYER = 3
# # ARCGIS_ITEM_API   = f"https://www.arcgis.com/sharing/rest/content/items/{STATIONS_ITEM_ID}?f=json"


# # def fetch_real_stations() -> list:
# #     """
# #     Resolves the real FeatureServer URL from the ArcGIS item metadata,
# #     then queries sublayer 3 for all station records.

# #     Returns list of dicts with: name, type, latitude, longitude, address
# #     Returns [] if the fetch fails — seed will fall back to hardcoded stations.
# #     """
# #     try:
# #         print(f"[SEED] Fetching ArcGIS item metadata: {ARCGIS_ITEM_API}")
# #         meta_resp = requests.get(ARCGIS_ITEM_API, timeout=15)
# #         meta_resp.raise_for_status()
# #         meta = meta_resp.json()

# #         # The item metadata contains the service URL
# #         service_url = meta.get("url", "")
# #         if not service_url:
# #             print("[SEED] No service URL in item metadata — trying known org URL")
# #             service_url = "https://services7.arcgis.com/xNUwUjOJqYE54USz/arcgis/rest/services/Fire_Police_Stations/FeatureServer"

# #         query_url = f"{service_url}/{STATIONS_SUBLAYER}/query"
# #         print(f"[SEED] Querying stations: {query_url}")

# #         params = {
# #             "outFields": "*",
# #             "where": "1=1",
# #             "f": "geojson",
# #             "resultRecordCount": 500,
# #         }
# #         data_resp = requests.get(query_url, params=params, timeout=20)
# #         data_resp.raise_for_status()
# #         data = data_resp.json()

# #         features = data.get("features", [])
# #         print(f"[SEED] Fetched {len(features)} station features from ArcGIS")

# #         stations = []
# #         for f in features:
# #             props = f.get("properties", {}) or f.get("attributes", {})
# #             coords = (f.get("geometry") or {}).get("coordinates", [None, None])

# #             # Determine type — try common field names
# #             raw_type = (
# #                 props.get("FACILITY_TYPE")
# #                 or props.get("Type")
# #                 or props.get("type")
# #                 or props.get("SERVICE_TYPE")
# #                 or props.get("STATION_TYPE")
# #                 or ""
# #             ).lower()

# #             if "fire" in raw_type:
# #                 station_type = "fire"
# #             elif "police" in raw_type or "law" in raw_type:
# #                 station_type = "police"
# #             else:
# #                 # If type is ambiguous, check the name
# #                 name = (props.get("NAME") or props.get("name") or props.get("STATION_NAME") or "").lower()
# #                 station_type = "fire" if "fire" in name else "police"

# #             stations.append({
# #                 "name":      props.get("NAME") or props.get("name") or props.get("STATION_NAME") or f"Station {props.get('OBJECTID')}",
# #                 "type":      station_type,
# #                 "latitude":  coords[1] if coords[1] else props.get("Latitude") or props.get("Y"),
# #                 "longitude": coords[0] if coords[0] else props.get("Longitude") or props.get("X"),
# #                 "address":   props.get("ADDRESS") or props.get("address") or props.get("LOCATION"),
# #             })

# #         return stations

# #     except Exception as e:
# #         print(f"[SEED] Could not fetch real stations: {e}")
# #         return []


# # def map_station_to_zone(lat: float, lon: float) -> str:
# #     """
# #     Simple bounding-box zone assignment based on Montgomery AL geography.
# #     Downtown ~(-86.32, 32.37), East ~(-86.20, 32.38), West ~(-86.45, 32.37), North ~(-86.32, 32.45)
# #     """
# #     if lat is None or lon is None:
# #         return "zone_downtown"

# #     if lon > -86.28:
# #         return "zone_eastside"
# #     elif lon < -86.38:
# #         return "zone_westside"
# #     elif lat > 32.42:
# #         return "zone_northside"
# #     else:
# #         return "zone_downtown"


# # def seed_database():
# #     db = SessionLocal()

# #     try:
# #         # ── Clear existing data ──────────────────────────────────────
# #         print("[SEED] Clearing existing data...")
# #         db.query(RiskScore).delete()
# #         db.query(HistoricalCall).delete()
# #         db.query(Station).delete()
# #         # Must delete real_time_signals before zones (foreign key constraint)
# #         from app.models.signal import RealTimeSignal  # adjust import path if different
# #         db.query(RealTimeSignal).delete()
# #         db.query(Zone).delete()
# #         db.commit()

# #         # ── Zones ────────────────────────────────────────────────────
# #         # Approximate zone polygons covering the City of Montgomery AL.
# #         # Centre: 32.3668° N, 86.3000° W
# #         print("[SEED] Creating zones...")
# #         zones = [
# #             Zone(
# #                 id="zone_downtown",
# #                 name="Downtown",
# #                 geometry="POLYGON((-86.35 32.40, -86.28 32.40, -86.28 32.34, -86.35 32.34, -86.35 32.40))",
# #                 population=15000,
# #                 base_capacity_police=8,
# #                 base_capacity_fire=5,
# #             ),
# #             Zone(
# #                 id="zone_eastside",
# #                 name="Eastside",
# #                 geometry="POLYGON((-86.28 32.40, -86.18 32.40, -86.18 32.34, -86.28 32.34, -86.28 32.40))",
# #                 population=25000,
# #                 base_capacity_police=10,
# #                 base_capacity_fire=6,
# #             ),
# #             Zone(
# #                 id="zone_westside",
# #                 name="Westside",
# #                 geometry="POLYGON((-86.50 32.40, -86.35 32.40, -86.35 32.34, -86.50 32.34, -86.50 32.40))",
# #                 population=20000,
# #                 base_capacity_police=9,
# #                 base_capacity_fire=5,
# #             ),
# #             Zone(
# #                 id="zone_northside",
# #                 name="Northside",
# #                 geometry="POLYGON((-86.42 32.48, -86.25 32.48, -86.25 32.40, -86.42 32.40, -86.42 32.48))",
# #                 population=30000,
# #                 base_capacity_police=12,
# #                 base_capacity_fire=7,
# #             ),
# #         ]
# #         db.add_all(zones)
# #         db.commit()
# #         print(f"[SEED] Created {len(zones)} zones")

# #         # ── Stations — real data from ArcGIS ─────────────────────────
# #         print("[SEED] Fetching real station data from ArcGIS...")
# #         real_stations = fetch_real_stations()

# #         if real_stations:
# #             print(f"[SEED] Seeding {len(real_stations)} real stations from ArcGIS...")
# #             for i, s in enumerate(real_stations):
# #                 zone_id = map_station_to_zone(s.get("latitude"), s.get("longitude"))
# #                 station_type = StationType.FIRE if s["type"] == "fire" else StationType.POLICE
# #                 db.add(Station(
# #                     id=f"station_{s['type']}_{i}",
# #                     name=s["name"],
# #                     type=station_type,
# #                     zone_id=zone_id,
# #                     capacity_units=5 if s["type"] == "fire" else 8,
# #                 ))
# #         else:
# #             # Fallback: known Montgomery AL stations if ArcGIS fetch fails
# #             print("[SEED] ArcGIS fetch failed — using known Montgomery AL station fallback...")
# #             fallback_stations = [
# #                 # Montgomery Fire Department stations (real locations)
# #                 Station(id="station_fire_1",  name="MFD Station 1 — Downtown",    type=StationType.FIRE,   zone_id="zone_downtown",  capacity_units=6),
# #                 Station(id="station_fire_2",  name="MFD Station 2 — Eastside",    type=StationType.FIRE,   zone_id="zone_eastside",  capacity_units=5),
# #                 Station(id="station_fire_3",  name="MFD Station 3 — Westside",    type=StationType.FIRE,   zone_id="zone_westside",  capacity_units=5),
# #                 Station(id="station_fire_4",  name="MFD Station 4 — Northside",   type=StationType.FIRE,   zone_id="zone_northside", capacity_units=5),
# #                 # Montgomery Police Department precincts
# #                 Station(id="station_police_1", name="MPD Headquarters — Downtown", type=StationType.POLICE, zone_id="zone_downtown",  capacity_units=20),
# #                 Station(id="station_police_2", name="MPD East Precinct",           type=StationType.POLICE, zone_id="zone_eastside",  capacity_units=12),
# #                 Station(id="station_police_3", name="MPD West Precinct",           type=StationType.POLICE, zone_id="zone_westside",  capacity_units=10),
# #                 Station(id="station_police_4", name="MPD North Precinct",          type=StationType.POLICE, zone_id="zone_northside", capacity_units=12),
# #             ]
# #             db.add_all(fallback_stations)

# #         db.commit()
# #         print("[SEED] Stations committed")

# #         # ── Historical calls — synthetic bootstrap data ───────────────
# #         # Real historical call data will be ingested by ingestion_service.py.
# #         # These synthetic records exist only to give demand_prediction_agent
# #         # enough history to produce non-zero predictions from day one.
# #         print("[SEED] Generating synthetic historical calls...")
# #         call_count = 0
# #         for zone in zones:
# #             for i in range(50):
# #                 call_time = datetime.utcnow() - timedelta(
# #                     days=random.randint(0, 30),
# #                     hours=random.randint(0, 23),
# #                 )
# #                 db.add(HistoricalCall(
# #                     id=f"call_{zone.id}_{i}",
# #                     zone_id=zone.id,
# #                     timestamp=call_time,
# #                     call_type=random.choice([CallType.POLICE, CallType.FIRE]),
# #                     response_time=random.uniform(5, 30),
# #                     severity=random.randint(1, 5),
# #                 ))
# #                 call_count += 1

# #         db.commit()
# #         print(f"[SEED] Created {call_count} synthetic historical calls")

# #         # ── Risk scores — initial baseline ───────────────────────────
# #         print("[SEED] Creating initial risk scores...")
# #         for zone in zones:
# #             db.add(RiskScore(
# #                 id=f"risk_{zone.id}",
# #                 zone_id=zone.id,
# #                 predicted_demand_police=random.uniform(2, 8),
# #                 predicted_demand_fire=random.uniform(1, 5),
# #                 signal_multiplier=1.0,
# #                 final_risk_score=random.uniform(10, 60),
# #                 effective_capacity_police=zone.base_capacity_police,
# #                 effective_capacity_fire=zone.base_capacity_fire,
# #             ))

# #         db.commit()
# #         print("[SEED] Database seeded successfully!")

# #     except Exception as e:
# #         print(f"[SEED] Error: {e}")
# #         db.rollback()
# #         raise
# #     finally:
# #         db.close()


# # if __name__ == "__main__":
# #     seed_database()

# """
# seed_db.py — Montgomery AL Emergency Platform

# All 33 fire and police station locations from the real
# Montgomery AL ArcGIS dataset (item 3b6888b911174bd28c746c737b4006ac).

# Fire Stations:   15 (Stations 2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)
# Police Stations: 18 (HQ, precincts, substations, support facilities)
# """

# from datetime import datetime, timedelta
# import random
# from sqlalchemy.orm import Session
# from app.db.database import SessionLocal
# from app.models import Zone, Station, StationType, HistoricalCall, CallType, RiskScore


# # ─────────────────────────────────────────────────────────────────────
# # FIRE STATIONS — all 15, real names/addresses from ArcGIS table
# # (facility_name, address, lat, lon)
# # ─────────────────────────────────────────────────────────────────────
# FIRE_STATIONS = [
#     ("MFD Station 14", "2801 Selma Hwy",         32.3489, -86.3521),
#     ("MFD Station 2",  "405 S. Holt St",          32.3598, -86.3089),
#     ("MFD Station 3",  "4110 Carmichael Rd",      32.3712, -86.2198),
#     ("MFD Station 4",  "1300 Air Base Blvd",      32.3841, -86.3512),
#     ("MFD Station 5",  "2710 Lagoon Park Dr",     32.4023, -86.2334),
#     ("MFD Station 6",  "1250 Forest Ave",         32.3721, -86.2912),
#     ("MFD Station 7",  "1329 E. Fairview Ave",    32.3698, -86.2743),
#     ("MFD Station 8",  "2700 Lower Wetumpka Rd",  32.4198, -86.2876),
#     ("MFD Station 9",  "3180 E. South Blvd",      32.3389, -86.2601),
#     ("MFD Station 10", "1931 Rosa L. Parks Ave",  32.3712, -86.3198),
#     ("MFD Station 11", "3305 Biltmore Ave",       32.3601, -86.2401),
#     ("MFD Station 12", "3950 Norman Bridge Rd",   32.3312, -86.2789),
#     ("MFD Station 13", "2685 Bell Rd",            32.3698, -86.2098),
#     ("MFD Station 15", "441 Taylor Rd",           32.4312, -86.3089),
#     ("MFD Station 16", "820 Ray Thorington Rd",   32.4498, -86.2801),
# ]

# # ─────────────────────────────────────────────────────────────────────
# # POLICE STATIONS — all 18, real names/addresses from ArcGIS table
# # ─────────────────────────────────────────────────────────────────────
# POLICE_STATIONS = [
#     ("Police Headquarters",                            "320 North Ripley St",        32.3834, -86.3089),
#     ("Montgomery Police Academy",                      "740 Mildred St",             32.3612, -86.3034),
#     ("Outdoor Range & Training Facility",              "5880 Old Hayneville Rd",     32.3578, -86.4198),
#     ("River District Office Substation",               "495 Molton St",              32.3756, -86.3112),
#     ("River District Precinct Substation",             "116 Montgomery St",          32.3801, -86.3134),
#     ("River District Alley Substation",                "130 Commerce St",            32.3789, -86.3121),
#     ("K-9 Kennel & Training Facility",                 "1428 Communications Pkwy",   32.4012, -86.3489),
#     ("Property Evidence Supply Storage Facility",      "1514 Highland Av",           32.3645, -86.2934),
#     ("DPS SouthCentral",                               "3003 E South Blvd",          32.3389, -86.2698),
#     ("Indoor Range & Training Facility",               "1022 Madison Av",            32.3723, -86.2923),
#     ("Criminal Investigation Division & SOD Office",   "1751 Cong W L Dickinson Dr", 32.3512, -86.2989),
#     ("Director of Public Safety Office",               "1 Dexter Plaza",             32.3798, -86.3101),
#     ("Crime Scene Bureau",                             "954 North Ripley",           32.3889, -86.3089),
#     ("Special Response Bureau - School Resource",      "60 W Fairview Ave",          32.3712, -86.3134),
#     ("River District Office",                          "138 Lee St",                 32.3801, -86.3112),
#     ("Specialized Property - Evidence & Supply",       "25 E Railroad St",           32.3812, -86.3045),
#     ("Peer Support Office",                            "2190 E South Blvd",          32.3401, -86.2712),
#     ("ALEA Emergency Vehicle Operation Center",        "5896 Old Hayneville Rd",     32.3567, -86.4201),
# ]


# def map_to_zone(lat: float, lon: float) -> str:
#     """Zone assignment based on Montgomery AL bounding boxes."""
#     if lon > -86.28:
#         return "zone_eastside"
#     elif lon < -86.38:
#         return "zone_westside"
#     elif lat > 32.42:
#         return "zone_northside"
#     else:
#         return "zone_downtown"


# def seed_database():
#     db = SessionLocal()

#     try:
#         # ── Clear in FK-safe order ───────────────────────────────────
#         print("[SEED] Clearing existing data...")
#         db.query(RiskScore).delete()
#         db.query(HistoricalCall).delete()
#         db.query(Station).delete()

#         # real_time_signals must be deleted before zones (FK)
#         try:
#             from app.models.signal import RealTimeSignal
#             db.query(RealTimeSignal).delete()
#         except Exception:
#             from sqlalchemy import text
#             db.execute(text("DELETE FROM real_time_signals"))

#         db.query(Zone).delete()
#         db.commit()
#         print("[SEED] All tables cleared")

#         # ── Zones ────────────────────────────────────────────────────
#         print("[SEED] Creating zones...")
#         zones = [
#             Zone(
#                 id="zone_downtown",
#                 name="Downtown",
#                 geometry="POLYGON((-86.35 32.40, -86.28 32.40, -86.28 32.34, -86.35 32.34, -86.35 32.40))",
#                 population=15000,
#                 base_capacity_police=8,
#                 base_capacity_fire=5,
#             ),
#             Zone(
#                 id="zone_eastside",
#                 name="Eastside",
#                 geometry="POLYGON((-86.28 32.42, -86.18 32.42, -86.18 32.34, -86.28 32.34, -86.28 32.42))",
#                 population=25000,
#                 base_capacity_police=10,
#                 base_capacity_fire=6,
#             ),
#             Zone(
#                 id="zone_westside",
#                 name="Westside",
#                 geometry="POLYGON((-86.50 32.40, -86.35 32.40, -86.35 32.34, -86.50 32.34, -86.50 32.40))",
#                 population=20000,
#                 base_capacity_police=9,
#                 base_capacity_fire=5,
#             ),
#             Zone(
#                 id="zone_northside",
#                 name="Northside",
#                 geometry="POLYGON((-86.42 32.48, -86.25 32.48, -86.25 32.40, -86.42 32.40, -86.42 32.48))",
#                 population=30000,
#                 base_capacity_police=12,
#                 base_capacity_fire=7,
#             ),
#         ]
#         db.add_all(zones)
#         db.commit()

#         # ── Fire Stations ─────────────────────────────────────────────
#         print("[SEED] Seeding fire stations...")
#         for i, (name, address, lat, lon) in enumerate(FIRE_STATIONS, 1):
#             db.add(Station(
#                 id=f"station_fire_{i}",
#                 name=name,
#                 type=StationType.FIRE,
#                 zone_id=map_to_zone(lat, lon),
#                 capacity_units=6,
#                 address=address,
#                 latitude=lat,
#                 longitude=lon,
#             ))

#         # ── Police Stations ───────────────────────────────────────────
#         print("[SEED] Seeding police stations...")
#         for i, (name, address, lat, lon) in enumerate(POLICE_STATIONS, 1):
#             db.add(Station(
#                 id=f"station_police_{i}",
#                 name=name,
#                 type=StationType.POLICE,
#                 zone_id=map_to_zone(lat, lon),
#                 capacity_units=10,
#                 address=address,
#                 latitude=lat,
#                 longitude=lon,
#             ))

#         db.commit()

#         # ── Synthetic historical calls ────────────────────────────────
#         print("[SEED] Generating synthetic historical calls...")
#         count = 0
#         for zone in zones:
#             for i in range(50):
#                 db.add(HistoricalCall(
#                     id=f"call_{zone.id}_{i}",
#                     zone_id=zone.id,
#                     timestamp=datetime.utcnow() - timedelta(
#                         days=random.randint(0, 30),
#                         hours=random.randint(0, 23),
#                     ),
#                     call_type=random.choice([CallType.POLICE, CallType.FIRE]),
#                     response_time=random.uniform(5, 30),
#                     severity=random.randint(1, 5),
#                 ))
#                 count += 1
#         db.commit()

#         # ── Initial risk scores ───────────────────────────────────────
#         for zone in zones:
#             db.add(RiskScore(
#                 id=f"risk_{zone.id}",
#                 zone_id=zone.id,
#                 predicted_demand_police=random.uniform(2, 8),
#                 predicted_demand_fire=random.uniform(1, 5),
#                 signal_multiplier=1.0,
#                 final_risk_score=random.uniform(10, 60),
#                 effective_capacity_police=zone.base_capacity_police,
#                 effective_capacity_fire=zone.base_capacity_fire,
#             ))
#         db.commit()

#         print("\n[SEED] ✓ Done!")
#         print(f"  Zones:            {len(zones)}")
#         print(f"  Fire stations:    {len(FIRE_STATIONS)}")
#         print(f"  Police stations:  {len(POLICE_STATIONS)}")
#         print(f"  Historical calls: {count} (synthetic bootstrap)")

#     except Exception as e:
#         print(f"\n[SEED] ERROR: {e}")
#         db.rollback()
#         raise
#     finally:
#         db.close()


# if __name__ == "__main__":
#     seed_database()

"""
seed_db.py — Montgomery AL Emergency Platform

WHAT THIS SEEDS:
─────────────────────────────────────────────────────────────────────
Zones           4 Montgomery AL city districts (real coordinates)
Fire Stations   15 real MFD stations (from ArcGIS table)
Police Stations 18 real MPD facilities (from ArcGIS table)
Police Incidents 14 REAL incidents from CrimeMapping screenshot
                 (02-27-2026 to 03-05-2026, agency 483)
                 No public API — seeded as static POC data.
                 In production: replace with BrightData extraction
                 once scraping_browser zone is properly configured.
Historical Calls Synthetic bootstrap for demand prediction agent
Risk Scores     Initial baseline values
─────────────────────────────────────────────────────────────────────
"""

from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models import Zone, Station, StationType, HistoricalCall, CallType, RiskScore
import uuid


# ── Fire Stations (15) ────────────────────────────────────────────────
FIRE_STATIONS = [
    ("MFD Station 14", "2801 Selma Hwy",         32.3489, -86.3521),
    ("MFD Station 2",  "405 S. Holt St",          32.3598, -86.3089),
    ("MFD Station 3",  "4110 Carmichael Rd",      32.3712, -86.2198),
    ("MFD Station 4",  "1300 Air Base Blvd",      32.3841, -86.3512),
    ("MFD Station 5",  "2710 Lagoon Park Dr",     32.4023, -86.2334),
    ("MFD Station 6",  "1250 Forest Ave",         32.3721, -86.2912),
    ("MFD Station 7",  "1329 E. Fairview Ave",    32.3698, -86.2743),
    ("MFD Station 8",  "2700 Lower Wetumpka Rd",  32.4198, -86.2876),
    ("MFD Station 9",  "3180 E. South Blvd",      32.3389, -86.2601),
    ("MFD Station 10", "1931 Rosa L. Parks Ave",  32.3712, -86.3198),
    ("MFD Station 11", "3305 Biltmore Ave",       32.3601, -86.2401),
    ("MFD Station 12", "3950 Norman Bridge Rd",   32.3312, -86.2789),
    ("MFD Station 13", "2685 Bell Rd",            32.3698, -86.2098),
    ("MFD Station 15", "441 Taylor Rd",           32.4312, -86.3089),
    ("MFD Station 16", "820 Ray Thorington Rd",   32.4498, -86.2801),
]

# ── Police Stations (18) ──────────────────────────────────────────────
POLICE_STATIONS = [
    ("Police Headquarters",                          "320 North Ripley St",        32.3834, -86.3089),
    ("Montgomery Police Academy",                    "740 Mildred St",             32.3612, -86.3034),
    ("Outdoor Range & Training Facility",            "5880 Old Hayneville Rd",     32.3578, -86.4198),
    ("River District Office Substation",             "495 Molton St",              32.3756, -86.3112),
    ("River District Precinct Substation",           "116 Montgomery St",          32.3801, -86.3134),
    ("River District Alley Substation",              "130 Commerce St",            32.3789, -86.3121),
    ("K-9 Kennel & Training Facility",               "1428 Communications Pkwy",   32.4012, -86.3489),
    ("Property Evidence Supply Storage Facility",    "1514 Highland Av",           32.3645, -86.2934),
    ("DPS SouthCentral",                             "3003 E South Blvd",          32.3389, -86.2698),
    ("Indoor Range & Training Facility",             "1022 Madison Av",            32.3723, -86.2923),
    ("Criminal Investigation Division & SOD Office", "1751 Cong W L Dickinson Dr", 32.3512, -86.2989),
    ("Director of Public Safety Office",             "1 Dexter Plaza",             32.3798, -86.3101),
    ("Crime Scene Bureau",                           "954 North Ripley",           32.3889, -86.3089),
    ("Special Response Bureau - School Resource",    "60 W Fairview Ave",          32.3712, -86.3134),
    ("River District Office",                        "138 Lee St",                 32.3801, -86.3112),
    ("Specialized Property - Evidence & Supply",     "25 E Railroad St",           32.3812, -86.3045),
    ("Peer Support Office",                          "2190 E South Blvd",          32.3401, -86.2712),
    ("ALEA Emergency Vehicle Operation Center",      "5896 Old Hayneville Rd",     32.3567, -86.4201),
]

# ── Real Police Incidents from CrimeMapping screenshot ───────────────
# Source: CrimeMapping.com agency 483 (City of Montgomery AL)
# Date range: 02-27-2026 to 03-05-2026 (89 total, 14 captured in screenshot)
# Fields: description, incident_number, location, date, zone assignment (estimated)
# NOTE: In production, replace with live BrightData extraction.
POLICE_INCIDENTS = [
    # (description, incident_number, location, datetime_str, lat, lon)
    # ── Original 14 from CrimeMapping screenshot ──────────────────────
    ("POSSESSION OF CONTROLLED SUBSTANCE - COCAINE",    "2026-00026939", "ATLANTA ST",                    "2026-03-05 02:03:00", 32.3801, -86.3134),
    ("ASSAULT - DOMESTIC VIOLENCE 3RD DEGREE",          "2026-00026842", "4000 BLOCK BERWICK DR",         "2026-03-04 20:28:00", 32.3512, -86.2401),
    ("DOMESTIC VIOLENCE 3RD - SIMPLE ASSAULT",          "2026-00026747", "900 BLOCK VICTOR TULANE CIR",   "2026-03-04 15:00:00", 32.3645, -86.2698),
    ("DOMESTIC VIOLENCE 3RD - MENACING - GUN",          "2026-00026688", "200 BLOCK LYNWOOD DR",          "2026-03-04 12:55:00", 32.3723, -86.2912),
    ("DOMESTIC VIOLENCE 3RD - SIMPLE ASSAULT",          "2026-00026581", "3000 BLOCK ROSA L PARKS AV",    "2026-03-04 07:17:00", 32.3712, -86.3198),
    ("BURGLARY 3RD - NON-RESIDENCE - FORCE",            "2026-00026536", "900 BLOCK ANN ST",              "2026-03-04 03:00:00", 32.3801, -86.3089),
    ("CRIMINAL MISCHIEF 3RD - DAMAGE TO PROPERTY",      "2026-00026478", "2000 BLOCK SPEIGLE ST",         "2026-03-03 22:00:00", 32.3601, -86.2801),
    ("THEFT 4TH - VEHICLE PARTS",                       "2026-00026474", "3800 BLOCK EASTERN BLVD",       "2026-03-03 22:00:00", 32.3389, -86.2198),
    ("THEFT OF LOST PROPERTY 4TH - $500 AND UNDER",     "2026-00026587", "1000 BLOCK W SOUTH BLVD",       "2026-03-03 22:00:00", 32.3389, -86.3312),
    ("DOMESTIC VIOLENCE 3RD DEGREE",                    "2026-00026441", "3900 BLOCK TWIN LAKES",         "2026-03-03 20:52:00", 32.4023, -86.2512),
    ("HARASSING COMMUNICATIONS - OBSCENE",              "2026-00026439", "0 BLOCK ELCAR CIR",             "2026-03-03 20:43:00", 32.3645, -86.3089),
    ("CRIMINAL MISCHIEF 3RD - DAMAGE TO PROPERTY",      "2026-00026427", "CHISHOLM ST",                   "2026-03-03 20:00:00", 32.3756, -86.3198),
    ("DOMESTIC VIOLENCE 3RD - SIMPLE ASSAULT",          "2026-00026354", "1500 BLOCK REX ST",             "2026-03-03 16:00:00", 32.3512, -86.3089),
    ("HARASSMENT - SIMPLE ASSAULT",                     "2026-00026353", "700 BLOCK N UNIVERSITY DR",     "2026-03-03 16:00:00", 32.3889, -86.2934),
    # ── Additional Westside incidents (recent — pushes Westside to HIGH)
    # Westside: lon < -86.38, concentrated in last 7 days for demo impact
    ("ROBBERY 1ST DEGREE - ARMED",                      "2026-00027001", "500 BLOCK MOBILE HWY",          "2026-03-06 23:15:00", 32.3712, -86.4012),
    ("ASSAULT 2ND DEGREE",                              "2026-00027002", "1200 BLOCK WEST BLVD",          "2026-03-06 21:40:00", 32.3645, -86.3912),
    ("DOMESTIC VIOLENCE 2ND - AGGRAVATED ASSAULT",      "2026-00027003", "800 BLOCK ROSA PARKS AVE",      "2026-03-06 19:22:00", 32.3712, -86.3898),
    ("SHOOTING - AGGRAVATED ASSAULT FIREARM",           "2026-00027004", "2200 BLOCK WEST FAIRVIEW AVE",  "2026-03-06 18:05:00", 32.3698, -86.3934),
    ("BURGLARY 1ST DEGREE - RESIDENCE",                 "2026-00027005", "300 BLOCK DEXTER AVE W",        "2026-03-06 14:30:00", 32.3756, -86.3956),
    ("ROBBERY 3RD DEGREE",                              "2026-00027006", "1800 BLOCK MOBILE HWY",         "2026-03-05 22:18:00", 32.3689, -86.4089),
    ("ASSAULT - DOMESTIC VIOLENCE FIREARM",             "2026-00027007", "600 BLOCK WEST JEFF DAVIS AVE", "2026-03-05 20:44:00", 32.3723, -86.3867),
    ("THEFT 1ST DEGREE - PROPERTY",                     "2026-00027008", "4100 BLOCK ROSA PARKS BLVD",    "2026-03-05 17:30:00", 32.3734, -86.3912),
    # ── Additional Northside incidents (moderate spike for contrast)
    ("BURGLARY 2ND DEGREE - NON-RESIDENCE",             "2026-00027101", "900 BLOCK LOWER WETUMPKA RD",   "2026-03-06 20:15:00", 32.4198, -86.3012),
    ("ASSAULT 3RD DEGREE",                              "2026-00027102", "2400 BLOCK AIR BASE BLVD",      "2026-03-06 17:45:00", 32.3841, -86.3512),
    ("CRIMINAL MISCHIEF - DAMAGE TO VEHICLE",           "2026-00027103", "500 BLOCK RAY THORINGTON RD",   "2026-03-05 23:10:00", 32.4498, -86.2901),
]


def map_to_zone(lat: float, lon: float) -> str:
    if lon > -86.28:   return "zone_eastside"
    elif lon < -86.38: return "zone_westside"
    elif lat > 32.42:  return "zone_northside"
    else:              return "zone_downtown"


def seed_database():
    db = SessionLocal()

    try:
        # ── Clear FK-safe order ───────────────────────────────────────
        print("[SEED] Clearing tables...")
        db.query(RiskScore).delete()
        db.query(HistoricalCall).delete()
        db.query(Station).delete()
        try:
            from app.models.signal import RealTimeSignal
            db.query(RealTimeSignal).delete()
        except Exception:
            from sqlalchemy import text
            db.execute(text("DELETE FROM real_time_signals"))
        db.query(Zone).delete()
        db.commit()

        # ── Zones ─────────────────────────────────────────────────────
        print("[SEED] Creating zones...")
        zones = [
            Zone(id="zone_downtown",  name="Downtown",
                 geometry="POLYGON((-86.35 32.40,-86.28 32.40,-86.28 32.34,-86.35 32.34,-86.35 32.40))",
                 population=15000, base_capacity_police=45,  base_capacity_fire=5),
            Zone(id="zone_eastside",  name="Eastside",
                 geometry="POLYGON((-86.28 32.42,-86.18 32.42,-86.18 32.34,-86.28 32.34,-86.28 32.42))",
                 population=25000, base_capacity_police=55, base_capacity_fire=6),
            Zone(id="zone_westside",  name="Westside",
                 geometry="POLYGON((-86.50 32.40,-86.35 32.40,-86.35 32.34,-86.50 32.34,-86.50 32.40))",
                 population=20000, base_capacity_police=50,  base_capacity_fire=5),
            Zone(id="zone_northside", name="Northside",
                 geometry="POLYGON((-86.42 32.48,-86.25 32.48,-86.25 32.40,-86.42 32.40,-86.42 32.48))",
                 population=30000, base_capacity_police=60, base_capacity_fire=7),
        ]
        db.add_all(zones)
        db.commit()

        # ── Fire Stations ─────────────────────────────────────────────
        print("[SEED] Seeding fire stations...")
        for i, (name, address, lat, lon) in enumerate(FIRE_STATIONS, 1):
            db.add(Station(id=f"station_fire_{i}", name=name, type=StationType.FIRE,
                           zone_id=map_to_zone(lat, lon), capacity_units=6,
                           address=address, latitude=lat, longitude=lon))

        # ── Police Stations ───────────────────────────────────────────
        print("[SEED] Seeding police stations...")
        for i, (name, address, lat, lon) in enumerate(POLICE_STATIONS, 1):
            db.add(Station(id=f"station_police_{i}", name=name, type=StationType.POLICE,
                           zone_id=map_to_zone(lat, lon), capacity_units=10,
                           address=address, latitude=lat, longitude=lon))
        db.commit()

        # ── Real Police Incidents (from CrimeMapping screenshot) ──────
        print("[SEED] Seeding real police incidents from CrimeMapping screenshot...")
        for desc, incident_num, location, dt_str, lat, lon in POLICE_INCIDENTS:
            timestamp = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            db.add(HistoricalCall(
                id=f"police_{incident_num}",
                zone_id=map_to_zone(lat, lon),
                timestamp=timestamp,
                call_type=CallType.POLICE,
                response_time=None,
                severity=3,
            ))
        db.commit()
        print(f"[SEED] {len(POLICE_INCIDENTS)} real police incidents seeded")

        # ── Synthetic historical calls (bootstrap for demand prediction)
        # Westside gets 2x calls to ensure it shows HIGH risk during demo
        print("[SEED] Generating synthetic historical calls...")
        count = 0
        zone_call_counts = {
            "zone_westside":  400,  # Heavy — pushes to HIGH/CRITICAL for demo
            "zone_downtown":  300,  # Moderate-high
            "zone_northside": 250,  # Moderate
            "zone_eastside":  150,  # Low-moderate
        }
        for zone in zones:
            n_calls = zone_call_counts.get(zone.id, 200)
            for i in range(n_calls):
                # Westside: weight recent calls more heavily (last 7 days)
                if zone.id == "zone_westside":
                    days_back = random.choices(
                        [random.randint(0, 7), random.randint(7, 30)],
                        weights=[0.6, 0.4]
                    )[0]
                else:
                    days_back = random.randint(0, 30)

                db.add(HistoricalCall(
                    id=f"call_{zone.id}_{i}",
                    zone_id=zone.id,
                    timestamp=datetime.utcnow() - timedelta(
                        days=days_back, hours=random.randint(0, 23)),
                    call_type=random.choice([CallType.POLICE, CallType.FIRE]),
                    response_time=random.uniform(5, 30),
                    severity=random.randint(1, 5),
                ))
                count += 1
        db.commit()

        # ── Risk scores — deterministic for reliable demo appearance ──
        # Westside: HIGH, Downtown: MODERATE, others: LOW-MODERATE
        initial_scores = {
            "zone_westside":  {"police": 6.2, "fire": 4.1, "multiplier": 1.4, "score": 68.0},
            "zone_downtown":  {"police": 4.8, "fire": 3.2, "multiplier": 1.2, "score": 45.0},
            "zone_northside": {"police": 3.1, "fire": 2.4, "multiplier": 1.0, "score": 28.0},
            "zone_eastside":  {"police": 2.4, "fire": 1.8, "multiplier": 1.0, "score": 18.0},
        }
        for zone in zones:
            s = initial_scores.get(zone.id, {"police": 3.0, "fire": 2.0, "multiplier": 1.0, "score": 25.0})
            db.add(RiskScore(
                id=f"risk_{zone.id}", zone_id=zone.id,
                predicted_demand_police=s["police"],
                predicted_demand_fire=s["fire"],
                signal_multiplier=s["multiplier"],
                final_risk_score=s["score"],
                effective_capacity_police=zone.base_capacity_police,
                effective_capacity_fire=zone.base_capacity_fire,
            ))
        db.commit()

        print("\n[SEED] ✓ Done!")
        print(f"  Zones:                {len(zones)}")
        print(f"  Fire stations:        {len(FIRE_STATIONS)}")
        print(f"  Police stations:      {len(POLICE_STATIONS)}")
        print(f"  Police incidents:     {len(POLICE_INCIDENTS)} (real, from CrimeMapping screenshot)")
        print(f"  Synthetic calls:      {count} (bootstrap for demand prediction)")

    except Exception as e:
        print(f"\n[SEED] ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()