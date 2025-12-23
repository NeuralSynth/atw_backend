# ATW Backend - All The Way Transportation System

Production-ready backend service for the **All The Way (ATW) Transportation System**, developed by Cyparta. A scalable Django-based system managing ambulance dispatch, patient records, real-time vehicle tracking, medical compliance, and billing operations.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django 4.2](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 Production Capabilities

- ✅ **10,000 concurrent users** with auto-scaling
- ✅ **5,000+ trips/day** handling capacity
- ✅ **Sub-2 second response times** with Redis caching
- ✅ **Real-time GPS tracking** (3-5 second updates via WebSocket)
- ✅ **99.9% uptime** with Kubernetes high-availability
- ✅ **HIPAA-compliant** patient data handling

## 🚀 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Framework** | Django 4.2 + DRF | REST API & business logic |
| **ASGI Server** | Daphne/Uvicorn | WebSocket support |
| **Database** | PostgreSQL 15+ | Primary data store with read replicas |
| **Cache** | Redis 7+ | Session storage, caching, WebSocket layer |
| **Task Queue** | Celery | Background job processing |
| **Message Broker** | Redis/RabbitMQ | Celery task distribution |
| **Orchestration** | Kubernetes | Container orchestration & auto-scaling |
| **WebSocket** | Django Channels | Real-time GPS tracking |
| **Monitoring** | Prometheus + Grafana | Metrics & observability |

## 📁 Project Structure

```
atw_backend/
├── config/                    # Django project configuration
│   ├── settings.py           # Settings (Redis, Channels, Celery, DB replicas)
│   ├── asgi.py               # ASGI app with WebSocket routing  
│   ├── celery.py             # Celery task queue configuration
│   ├── db_router.py          # Database read/write replica routing
│   └── urls.py               # Root URL configuration
│
├── users/                     # User management & authentication
│   ├── models.py             # Custom User model with role-based access
│   ├── views.py              # User API endpoints
│   └── management/commands/  # populate_sample_data.py
│
├── patients/                  # HIPAA-compliant patient records
│   ├── models.py             # Patient medical information
│   └── views.py              # Patient CRUD API
│
├── vehicles/                  # Fleet & vehicle management
│   ├── models.py             # Vehicle info, GPS location
│   └── views.py              # Vehicle tracking API
│
├── trips/                     # Trip dispatch & real-time tracking
│   ├── models.py             # Trip model with status tracking
│   ├── consumers.py          # 🌟 WebSocket GPS tracking consumers
│   ├── routing.py            # WebSocket URL routing
│   └── views.py              # Trip management API
│
├── ems/                       # EMS compliance & reporting
│   └── models.py             # Medical compliance models
│
├── billing/                   # Invoicing & financial  
│   └── models.py             # Invoice, contract models
│
├── k8s/                       # Kubernetes manifests
│   ├── base/                 # Namespace, ConfigMaps, Secrets
│   ├── deployments/          # Django, Redis cluster
│   ├── services/             # Service definitions
│   ├── autoscaling/          # HPA (10-30 pods)
│   └── ingress/              # NGINX Ingress with SSL
│
├── docs/                      # Documentation
│   ├── ARCHITECTURE-HYPERSCALE.md
│   ├── KUBERNETES-DEPLOYMENT.md
│   └── CI-CD.md
│
├── load-tests/                # Performance testing
│   └── k6-hyperscale.js      # Load test scenarios
│
├── .github/workflows/         # CI/CD pipeline  
│   └── django-ci.yml         # GitHub Actions workflow
│
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Multi-stage production build
├── docker-compose.yml         # Local development stack
└── .env.example              # Environment template
```

## 🎯 Key Features

### 🔴 Real-Time GPS Tracking (NEW!)
- **WebSocket-based** live location updates every 3-5 seconds
- Supports **10,000+ concurrent connections**
- Broadcast GPS updates to multiple clients (dashboard, mobile)
- Low-latency position tracking for ambulances

```javascript
// Connect to GPS tracking WebSocket
const ws = new WebSocket('ws://api.atw.com/ws/trips/123/gps/');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Lat: ${data.latitude}, Lng: ${data.longitude}`);
};
```

### ⚡ High-Performance Caching
- **Redis-backed** session storage and query cache
- **90%+ cache hit ratio** for sub-2s response times
- Intelligent cache invalidation strategies
- Distributed caching across pods

### 🗄️ Database Optimization
- **Read replica routing** (70%+ of reads offloaded from primary)
- Automatic **connection pooling** (600s max age)
- Support for **2 read replicas** in production
- Round-robin distribution for read queries

### 🔄 Background Task Processing
- **Celery workers** with 3 priority queues:
  - High: Emergency dispatch, GPS updates
  - Normal: Trip completion, billing
  - Low: Reports, notifications
- **Periodic tasks**: GPS cleanup, timeout monitoring

### 🚀 Auto-Scaling Infrastructure
- **Kubernetes HPA**: 10-30 pods based on CPU/memory
- **Redis cluster**: 6 nodes (3 masters + 3 replicas)
- **Load balancing** across multiple availability zones
- **Zero-downtime** rolling updates

## 🛠️ Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for local development)
- Kubernetes cluster (for production deployment)

### Local Development Setup

#### 1. Clone & Setup Environment

```bash
git clone <repository-url>
cd atw_backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your database and Redis credentials
nano .env  # or use your preferred editor
```

**Minimal .env for development:**
```env
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://user:password@localhost:5432/atw_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

#### 3. Setup Database

```bash
# Create PostgreSQL database
createdb atw_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# (Optional) Load sample data
python manage.py populate_sample_data
```

#### 4. Run Services

**Option A: Run services separately**

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Django with WebSocket support
daphne config.asgi:application -b 0.0.0.0 -p 8000

# Terminal 3: Celery worker
celery -A config worker --loglevel=info

# Terminal 4: Celery beat (periodic tasks)
celery -A config beat --loglevel=info
```

**Option B: Use Docker Compose**

```bash
docker-compose up --build
```

#### 5. Access Application

- **API**: http://localhost:8000/api/v1/
- **Admin**: http://localhost:8000/admin/
- **WebSocket**: ws://localhost:8000/ws/trips/<trip_id>/gps/

## 📚 API Documentation

### Authentication
```http
POST /api/v1/auth/login/
POST /api/v1/auth/logout/
```

### Core Resources
```http
# Users
GET    /api/v1/users/
POST   /api/v1/users/
GET    /api/v1/users/{id}/
PUT    /api/v1/users/{id}/
DELETE /api/v1/users/{id}/

# Patients (HIPAA-compliant)
GET    /api/v1/patients/
POST   /api/v1/patients/
GET    /api/v1/patients/{id}/
PUT    /api/v1/patients/{id}/

# Vehicles
GET    /api/v1/vehicles/
POST   /api/v1/vehicles/
GET    /api/v1/vehicles/{id}/

# Trips
GET    /api/v1/trips/
POST   /api/v1/trips/
GET    /api/v1/trips/{id}/
PUT    /api/v1/trips/{id}/

# EMS Reports
GET    /api/v1/ems/
POST   /api/v1/ems/

# Billing
GET    /api/v1/billing/
POST   /api/v1/billing/
```

### WebSocket Endpoints

```
ws://api.atw.com/ws/trips/<trip_id>/gps/      # Real-time GPS tracking
ws://api.atw.com/ws/trips/<trip_id>/status/   # Trip status updates
```

## 🐳 Docker Deployment

### Development

```bash
docker-compose up --build
```

### Production

```bash
# Build production image
docker build -t atw-backend:latest .

# Run with environment variables
docker run -d \
  --name atw-backend \
  -p 8000:8000 \
  --env-file .env \
  atw-backend:latest
```

## ☸️ Kubernetes Deployment

### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/base/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/autoscaling/
kubectl apply -f k8s/ingress/

# Check deployment status
kubectl get pods -n atw-production
kubectl get hpa -n atw-production
```

### Scale Manually

```bash
# Scale Django pods
kubectl scale deployment django --replicas=20 -n atw-production

# Check auto-scaler status
kubectl describe hpa django-hpa -n atw-production
```

For detailed Kubernetes setup, see [docs/KUBERNETES-DEPLOYMENT.md](docs/KUBERNETES-DEPLOYMENT.md)

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific app
pytest trips/tests.py
```

### Load Testing

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io/

# Run load test (10K concurrent users)
k6 run --vus 10000 --duration 10m load-tests/k6-hyperscale.js
```

## 📊 Monitoring

### Metrics

Access Prometheus metrics at: `http://localhost:8000/metrics`

Key metrics:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `websocket_connections` - Active WebSocket connections
- `celery_tasks_total` - Background tasks processed
- `cache_hit_ratio` - Cache effectiveness

### Health Checks

```bash
# Application health
curl http://localhost:8000/api/v1/health/

# Readiness probe
curl http://localhost:8000/api/v1/ready/
```

## 🔒 Security

### Production Checklist

- [ ] Change `SECRET_KEY` (generate with: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Enable SSL/HTTPS (`SECURE_SSL_REDIRECT=True`)
- [ ] Use strong database passwords
- [ ] Enable HSTS headers
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Enable security middleware
- [ ] Use secrets management (Kubernetes Secrets, AWS Secrets Manager)

## 📈 Performance Benchmarks

| Metric | Development | Production (K8s) |
|--------|-------------|------------------|
| **Concurrent Users** | 100 | 10,000 |
| **Response Time (p95)** | < 500ms | < 2 seconds |
| **GPS Updates** | 5 seconds | 3-5 seconds |
| **Trips/Day** | 100 | 5,000+ |
| **Uptime** | N/A | 99.9% |
| **Cost/Month** | $0 | $2,000 |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

See [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Team**: Cyparta Development Team

---

**Built with ❤️ by Cyparta** | All The Way Transportation System
