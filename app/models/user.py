from sqlalchemy import Column, String, DateTime, Enum
from datetime import datetime
import enum
from app.db.database import Base


class UserRole(str, enum.Enum):
    # Government roles
    POLICE_ADMIN = "police_admin"
    FIRE_ADMIN = "fire_admin"
    EMERGENCY_MANAGER = "emergency_manager"
    # Civilian roles
    RESIDENT = "resident"
    BUSINESS_OWNER = "business_owner"
    EVENT_ORGANIZER = "event_organizer"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(Enum(UserRole), default=UserRole.RESIDENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
