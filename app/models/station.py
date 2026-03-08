# from sqlalchemy import Column, String, Integer, ForeignKey, Enum, DateTime
# from sqlalchemy.orm import relationship
# from datetime import datetime
# import enum
# from app.db.database import Base


# class StationType(str, enum.Enum):
#     POLICE = "police"
#     FIRE = "fire"


# class Station(Base):
#     __tablename__ = "stations"

#     id = Column(String, primary_key=True, index=True)
#     name = Column(String, index=True)
#     type = Column(Enum(StationType))
#     zone_id = Column(String, ForeignKey("zones.id"))
#     capacity_units = Column(Integer)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     zone = relationship("Zone", back_populates="stations")
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class StationType(str, enum.Enum):
    POLICE = "police"
    FIRE = "fire"


class Station(Base):
    __tablename__ = "stations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(Enum(StationType))
    zone_id = Column(String, ForeignKey("zones.id"))
    capacity_units = Column(Integer)
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    zone = relationship("Zone", back_populates="stations")