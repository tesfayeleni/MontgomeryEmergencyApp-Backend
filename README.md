# Backend API Server

**Version:** 1.0.0  
**Framework:** FastAPI (Python)  
**Database:** PostgreSQL + PostGIS  
**Status:** Production-Ready

The backend provides RESTful APIs for emergency intelligence, data ingestion, authentication, and citizen services. Built with FastAPI for high performance and automatic OpenAPI documentation.

## 🚀 Quick Setup

### Prerequisites
- Python 3.9+
- PostgreSQL with PostGIS extension
- BrightData API key (provided)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Download NLP model
python -m spacy download en_core_web_sm

# Configure environment (optional)
cp .env.example .env
# Database and API keys already configured
```

### Run Server
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access Points:**
- **API Server:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## 🏗️ Architecture

### Core Components
- **main.py:** FastAPI application with CORS, routing, and scheduler
- **app/models/:** SQLAlchemy ORM models for database entities
- **app/api/:** REST API route handlers
- **app/agents/:** Intelligence agents for forecasting and risk scoring
- **app/data_ingestion/:** BrightData API client and ingestion services
- **app/auth/:** JWT authentication and role-based access control

### Key Technologies
- **FastAPI:** High-performance async web framework
- **SQLAlchemy:** ORM with PostgreSQL + PostGIS support
- **APScheduler:** Background job scheduling
- **scikit-learn:** Machine learning for demand forecasting
- **spaCy:** Natural language processing
- **BrightData:** Web scraping and API integration
- **GeoAlchemy2:** Geospatial database operations

## 📊 Data Models

### Core Entities
- **User:** Authentication with role-based permissions
- **Zone:** Geographic areas with capacity metrics
- **Station:** Fire/police station locations and capabilities
- **HistoricalCall:** 911 call history for training models
- **PoliceIncident:** Real-time incident data
- **ZoneRisk:** Calculated risk scores per zone
- **CitizenReport:** Non-emergency community submissions
- **RealTimeSignal:** News, events, and alerts
- **Event:** Large gathering notifications

### Relationships
- Zones contain stations and historical calls
- Risk scores calculated from predictions, signals, and capacity
- Users have role-based access to different endpoints

## 🔌 API Endpoints

### Authentication (`/auth`)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| POST | `/auth/login` | User authentication | Public |
| POST | `/auth/register` | User registration | Public |
| GET | `/auth/me` | Current user profile | Authenticated |

### Intelligence (`/api`)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/api/forecast` | 6-hour demand predictions | Government |
| GET | `/api/risk` | Zone risk scores | All users |
| GET | `/api/signals` | Real-time intelligence signals | Government |
| POST | `/api/run-agents` | Manual agent execution | Emergency Manager |

### Citizen Services (`/citizen`)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| POST | `/citizen/report` | Submit safety concerns | Citizens |
| POST | `/citizen/event` | Submit event notifications | Event Organizers |
| GET | `/citizen/public-feed` | Public safety information | All users |

### Zones (`/zones`)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| GET | `/zones/` | List all zones | Authenticated |
| GET | `/zones/{id}` | Zone details | Authenticated |

### Data Ingestion (`/data-ingestion`)
| Method | Endpoint | Description | Access |
|--------|----------|-------------|---------|
| POST | `/data-ingestion/ingest-brightdata` | Manual data refresh | Emergency Manager |
| GET | `/data-ingestion/status` | Ingestion statistics | Emergency Manager |
| GET | `/data-ingestion/test` | API connectivity test | Emergency Manager |

## 🤖 Intelligence Agents

### DemandPredictionAgent
- **Schedule:** Every 15 minutes
- **Purpose:** Forecast 6-hour resource demand using gradient boosting
- **Input:** Historical call data, time features, zone characteristics
- **Output:** Police, Fire, EMS demand predictions per zone

### SignalFusionAgent
- **Schedule:** Every 10 minutes
- **Purpose:** Aggregate real-time signals from multiple sources
- **Input:** Citizen reports, news feeds, event notifications
- **Output:** Weighted signal multipliers for risk calculation

### RiskScoringAgent
- **Schedule:** Every 5 minutes
- **Purpose:** Calculate dynamic risk scores per zone
- **Formula:** `(Predicted Demand × Signal Multiplier) / Effective Capacity`
- **Scale:** 0-100 (higher = greater risk)

### DataIngestionAgent
- **Schedule:** Every 10 minutes
- **Purpose:** Fetch fresh data from Montgomery APIs
- **Sources:** Police incidents, 911 calls, station locations

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://postgres:1Lalufiker#@db.fsswiqmfurgsxjkobktk.supabase.co:5432/postgres

# BrightData API
BRIGHTDATA_API_KEY=1a56b3bd-f3d0-4b38-8479-103ca3bd1a4e

# Security
SECRET_KEY=your-secret-key-here
DEBUG=true

# Optional
OPENAI_API_KEY=your-openai-key  # For enhanced NLP features
```

### Database Setup
```bash
# Create database with PostGIS
createdb montgomery_emergency
psql montgomery_emergency -c "CREATE EXTENSION postgis;"

# Run migrations
python -c "from app.db.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Seed sample data (optional)
python seed_db.py
```

## 🧪 Testing

### Automated Tests
```bash
# Run API endpoint tests
python ../test_endpoints.py

# Test specific endpoints
curl -X GET http://localhost:8000/data-ingestion/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Default Test Users
```
Admin: admin@montgomery.gov / admin123 (emergency_manager)
Citizen: resident@example.com / resident123 (resident)
```

## 📊 Data Ingestion

### Sources
- **Police Incidents:** Montgomery County Socrata API
- **911 Calls:** Montgomery AL ArcGIS REST API
- **Stations:** Montgomery AL ArcGIS REST API
- **Traffic:** Montgomery AL ArcGIS REST API

### Process
1. Fetch raw data from APIs
2. Parse and normalize fields
3. Map locations to zones using PostGIS
4. Store in database with timestamps
5. Trigger intelligence agents

## 🚀 Deployment

### Docker
```bash
docker build -t montgomery-backend .
docker run -p 8000:8000 montgomery-backend
```

### Production
- Use Gunicorn instead of uvicorn
- Configure reverse proxy (nginx)
- Set up database backups
- Enable monitoring and logging
- Use environment-specific configs

## 📈 Performance

### Capabilities
✅ High-performance async APIs  
✅ Real-time data processing  
✅ Machine learning inference  
✅ Geospatial queries  
✅ JWT authentication  
✅ Background job scheduling  
✅ Automatic API documentation  

### Limitations
❌ Not designed for 911 call handling  
❌ No real-time vehicle tracking  
❌ Limited to Montgomery County data  
❌ Requires stable API access  

## 🆘 Troubleshooting

- **Database Connection:** Check DATABASE_URL and PostGIS extension
- **BrightData Issues:** Verify API key and network connectivity
- **ML Models:** Ensure scikit-learn and spaCy are installed
- **Scheduler:** Check APScheduler logs for job execution

## 📚 Dependencies

### Core
- fastapi==0.104.1
- uvicorn==0.24.0
- sqlalchemy==2.0.23
- psycopg2-binary==2.9.9

### ML & NLP
- scikit-learn==1.3.2
- spacy==3.7.2
- numpy==1.24.3

### Data & APIs
- brightdata==0.4.0.4
- requests==2.31.0
- geoalchemy2==0.14.1

### Utils
- python-dotenv==1.0.0
- pyjwt==2.8.1
- apscheduler==3.10.4

---

**API Docs:** http://localhost:8000/docs  
**Health Check:** http://localhost:8000/health  
**Version:** 1.0.0
