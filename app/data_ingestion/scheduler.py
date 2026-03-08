from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from app.data_ingestion.ingestion_service import DataIngestionService
from app.agents.demand_prediction import DemandPredictionAgent
from app.agents.signal_fusion import SignalFusionAgent
from app.agents.risk_scoring import RiskScoringAgent
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SchedulerManager:
    """
    Manages background jobs for:
    - Continuous BrightData ingestion
    - Agent re-training
    - Risk score updates
    """

    def __init__(self, db_session_factory):
        self.db_factory = db_session_factory
        self.scheduler = BackgroundScheduler()
        self.running = False

    def ingest_data_job(self):
        """Background job for data ingestion"""
        try:
            db = self.db_factory()
            service = DataIngestionService(db)
            result = service.run_full_ingestion()
            logger.info(f"Data ingestion job completed: {result}")
            db.close()
        except Exception as e:
            logger.error(f"Error in data ingestion job: {e}")

    def predict_demand_job(self):
        """Background job for demand prediction"""
        try:
            db = self.db_factory()
            agent = DemandPredictionAgent(db)
            agent.run()
            logger.info("Demand prediction job completed")
            db.close()
        except Exception as e:
            logger.error(f"Error in demand prediction job: {e}")

    def update_signals_job(self):
        """Background job for signal fusion"""
        try:
            db = self.db_factory()
            agent = SignalFusionAgent(db)
            agent.run()
            logger.info("Signal fusion job completed")
            db.close()
        except Exception as e:
            logger.error(f"Error in signal fusion job: {e}")

    def update_risk_scores_job(self):
        """Background job for risk score calculation"""
        try:
            db = self.db_factory()
            agent = RiskScoringAgent(db)
            agent.run()
            logger.info("Risk scoring job completed")
            db.close()
        except Exception as e:
            logger.error(f"Error in risk scoring job: {e}")

    def start(self):
        """Start all background jobs"""
        if self.running:
            logger.warning("Scheduler already running")
            return

        try:
            # Data ingestion: every 60 minutes
            self.scheduler.add_job(
                self.ingest_data_job,
                IntervalTrigger(minutes=60),
                id="brightdata_ingest",
                name="BrightData Data Ingestion",
                misfire_grace_time=60
            )

            # Demand prediction: every 15 minutes
            self.scheduler.add_job(
                self.predict_demand_job,
                IntervalTrigger(minutes=15),
                id="demand_predict",
                name="Demand Prediction",
                misfire_grace_time=30
            )

            # Signal fusion: every 10 minutes
            self.scheduler.add_job(
                self.update_signals_job,
                IntervalTrigger(minutes=10),
                id="signal_fusion",
                name="Signal Fusion",
                misfire_grace_time=30
            )

            # Risk scoring: every 5 minutes
            self.scheduler.add_job(
                self.update_risk_scores_job,
                IntervalTrigger(minutes=5),
                id="risk_scoring",
                name="Risk Scoring",
                misfire_grace_time=30
            )

            self.scheduler.start()
            self.running = True
            logger.info("Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")

    def stop(self):
        """Stop all background jobs"""
        if self.running:
            self.scheduler.shutdown(wait=False)
            self.running = False
            logger.info("Scheduler stopped")
