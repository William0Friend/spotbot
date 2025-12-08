# SpotBot - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### 1. Set Up Environment

```bash
# Clone the repository (if you haven't already)
# cd spotbot

# Copy environment file
cp .env.example .env

# Edit .env if you want to customize settings (optional for local dev)
```

### 2. Start All Services

```bash
# Build and start all containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

This will start:
- **PostgreSQL** (Database) - Port 5432
- **Redis** (Cache) - Port 6379
- **Backend API** (FastAPI) - Port 8000
- **AI Detector** (ML Service) - Port 8001
- **Frontend** (React) - Port 3000

### 3. Access the Application

- **Frontend Web App**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **AI Detector API**: http://localhost:8001/docs

## 🧪 Testing the Application

### Test 1: Check Services Health

```bash
# Check backend health
curl http://localhost:8000/health

# Check AI detector health
curl http://localhost:8001/health
```

### Test 2: Analyze Text Content

1. Open http://localhost:3000/detect
2. Select "Text" content type
3. Paste this AI-generated sample:

```
As an AI language model, I don't have personal experiences or feelings. However, I can provide you with information about this topic. It's important to note that this is a complex subject with various perspectives. Let me help you understand the key points step-by-step.
```

4. Click "Analyze Content"
5. View confidence scores and detected model

### Test 3: Analyze Image URL

1. Select "Image" content type
2. Enter an image URL (try any online image)
3. Get AI detection results

### Test 4: Check History

1. Go to http://localhost:3000/history
2. View all your previous analyses

## 📝 API Testing with cURL

### Analyze Text via API

```bash
curl -X POST http://localhost:8000/api/v1/detect/ \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "text",
    "content_text": "As an AI language model, I cannot provide personal opinions."
  }'
```

### Register a User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

## 🛠️ Development Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ai-detector
docker-compose logs -f frontend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Access Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U spotbot -d spotbot

# View tables
\dt

# Query submissions
SELECT * FROM submissions;
```

### Access Container Shell

```bash
# Backend shell
docker-compose exec backend /bin/bash

# AI detector shell
docker-compose exec ai-detector /bin/bash

# Frontend shell
docker-compose exec frontend /bin/sh
```

## 🐛 Troubleshooting

### Issue: Port already in use

```bash
# Find process using port
lsof -i :3000  # or :8000, :8001
# Kill the process or change port in docker-compose.yml
```

### Issue: Database connection fails

```bash
# Check if postgres is running
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres
```

### Issue: Frontend can't connect to backend

1. Check if backend is running: http://localhost:8000/health
2. Verify VITE_API_URL in docker-compose.yml
3. Check browser console for CORS errors

### Issue: AI detector service fails

```bash
# Check logs
docker-compose logs ai-detector

# The first run may take time to download ML models
# Wait for "Application startup complete" message
```

## 📦 Project Structure

```
spotbot/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Config, database, security
│   │   ├── models/      # SQLAlchemy models
│   │   └── schemas/     # Pydantic schemas
│   └── Dockerfile
│
├── ai-detector/         # ML inference service
│   ├── app/
│   │   ├── detectors/   # Detection algorithms
│   │   └── main.py
│   └── Dockerfile
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── pages/       # Page components
│   │   ├── api/         # API client
│   │   └── store/       # State management
│   └── Dockerfile
│
├── database/            # Database initialization
│   └── init.sql
│
└── docker-compose.yml   # Service orchestration
```

## 🔑 Key Features Implemented

### Phase 1 (Current)
- ✅ Multi-format content detection (text, image, URL, video)
- ✅ AI confidence scoring (0-100%)
- ✅ Model identification (GPT, Claude, Gemini, etc.)
- ✅ User authentication and registration
- ✅ Detection history tracking
- ✅ RESTful API with automatic documentation
- ✅ Docker-based development environment

### Next Steps (Phase 2)
- 🔄 Improved ML models for detection
- 🔄 File upload support
- 🔄 Crowdsourced reporting
- 🔄 Bot network tracking
- 🔄 API rate limiting
- 🔄 Dashboard analytics

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Database Schema**: See `database/init.sql`
- **Frontend Routes**: See `frontend/src/App.jsx`

## 🤝 Contributing

Ready to add new features? Here's how:

1. Create a new feature branch
2. Make your changes
3. Test with `docker-compose up --build`
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.

---

**Need Help?** Check the logs with `docker-compose logs -f` or open an issue on GitHub.
