from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.zone import Zone
from app.models.station import Station

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("/")
async def get_zones(db: Session = Depends(get_db)) -> List[dict]:
    """Get all zones with basic info"""
    zones = db.query(Zone).all()
    
    return [
        {
            "id": z.id,
            "name": z.name,
            "population": z.population,
            "base_capacity_police": z.base_capacity_police,
            "base_capacity_fire": z.base_capacity_fire,
        }
        for z in zones
    ]


@router.get("/{zone_id}")
async def get_zone_detail(zone_id: str, db: Session = Depends(get_db)):
    """Get detailed zone information"""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    
    if not zone:
        return {"error": "Zone not found"}
    
    stations = db.query(Station).filter(Station.zone_id == zone_id).all()
    
    return {
        "id": zone.id,
        "name": zone.name,
        "population": zone.population,
        "base_capacity_police": zone.base_capacity_police,
        "base_capacity_fire": zone.base_capacity_fire,
        "stations": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type.value,
                "capacity_units": s.capacity_units,
            }
            for s in stations
        ],
    }
