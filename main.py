from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.db.database import engine, Base, get_db, SessionLocal
from app.api import auth_router, intelligence_router, citizen_router, zones_router
from app.data_ingestion.routes import router as data_ingestion_router
from app.data_ingestion.scheduler import SchedulerManager
from app.models import *
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Montgomery Emergency Intelligence Platform",
    description="Real-time emergency demand forecasting and signal fusion",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://montgomery-emergency-app-frontend.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(intelligence_router)
app.include_router(citizen_router)
app.include_router(zones_router)
app.include_router(data_ingestion_router)

# Initialize scheduler
scheduler_manager = SchedulerManager(SessionLocal)


@app.on_event("startup")
async def startup_event():
    """Start background scheduler on app startup"""
    logger.info("Starting Montgomery Emergency Intelligence Platform")
    logger.info(f"BrightData API configured: {bool(os.getenv('BRIGHTDATA_API_KEY'))}")
    scheduler_manager.start()
    logger.info("Background scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler on app shutdown"""
    logger.info("Shutting down Montgomery Emergency Intelligence Platform")
    scheduler_manager.stop()
    logger.info("Background scheduler stopped")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scheduler_running": scheduler_manager.running,
        "timestamp": os.popen("date").read().strip()
    }


@app.get("/")
async def root():
    """API documentation"""
    return {
        "name": "Montgomery Emergency Intelligence Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "brightdata_integrated": bool(os.getenv("BRIGHTDATA_API_KEY")),
        "features": [
            "Real-time demand forecasting",
            "BrightData continuous data ingestion",
            "Signal fusion and intelligence",
            "Risk scoring and heatmapping",
            "Role-based access control",
            "Government and citizen dashboards"
        ]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
