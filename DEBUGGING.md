# SpotBot Debugging Guide

## FastAPI Debugging Tools (Laravel Telescope Alternatives)

SpotBot includes several debugging tools similar to Laravel Telescope for development:

### 1. Built-in Request/Response Logging

All requests and responses are automatically logged with:
- Request method and path
- Client IP address
- Request headers
- Response status codes
- Processing time
- Full error tracebacks

**Check logs:**
```bash
# View backend logs
docker-compose logs -f backend

# View AI detector logs
docker-compose logs -f ai-detector

# View all logs
docker-compose logs -f
```

### 2. Debug Endpoints

#### List All Routes
```bash
curl http://localhost:8000/debug/routes
```
Shows all available API routes (like Laravel's `route:list`)

#### Health Check with Debug Info
```bash
curl http://localhost:8000/health
```

### 3. Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These allow you to:
- Test all endpoints interactively
- See request/response schemas
- View example payloads
- Execute requests directly from browser

### 4. Rate Limiting & Monitoring

SpotBot uses `slowapi` for rate limiting (like Laravel's throttle):
- 100 requests per minute on health endpoint
- Custom limits can be added to any endpoint
- Rate limit information included in response headers

### 5. Custom Response Headers

Every response includes debug headers:
- `X-Process-Time`: Request processing duration
- `X-Debug-Mode`: Indicates debug mode is enabled

### 6. Enhanced Error Messages

All errors return detailed JSON with:
- Error detail/message
- Request path and method
- Status code
- Timestamp
- Full traceback (in development)

## Testing Your AI Detection

### Test Text Detection

```bash
# Test with ChatGPT-style text
curl -X POST http://localhost:8000/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "text",
    "content_text": "Certainly! It'\''s worth noting that this is an important topic. However, we must consider various factors. Moreover, it'\''s crucial to understand the implications."
  }'
```

### Test with Your Sample Text

```bash
curl -X POST http://localhost:8000/api/v1/detect \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "text",
    "content_text": "Nice idea — high-impact and hard in all the right ways. I'\''ll lay out a practical, citation-backed plan you can build from: what the product is, how detection/attribution actually works today (and its limits), a concrete system architecture (MVP → production), data & tooling choices, legal/privacy concerns, evaluation, and a suggested 90-day roadmap. I'\''ll call the product \"SpotBot\" in examples."
  }'
```

### Direct AI Detector Test

```bash
# Test AI detector service directly
curl -X POST http://localhost:8001/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "text",
    "content_text": "Your text here"
  }'
```

## Common Issues & Solutions

### Issue: "Analysis Failed" Error

**Causes:**
1. AI detector service is not running
2. Network connectivity issues between services
3. Invalid request format

**Debug:**
```bash
# Check if AI detector is running
docker-compose ps

# View AI detector logs
docker-compose logs ai-detector

# Test AI detector directly
curl http://localhost:8001/health
```

### Issue: Backend Database Errors

**Cause:** Missing `psycopg2` dependency (now fixed)

**Solution:** Rebuild backend container:
```bash
docker-compose down
docker-compose up --build backend
```

### Issue: Frontend Can't Connect to Backend

**Debug:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check CORS settings in logs
docker-compose logs backend | grep CORS

# Verify API endpoint
curl http://localhost:8000/api/v1/detect/test
```

## Advanced Debugging

### Using Python Debugger (pdb)

Add to any Python file:
```python
import pdb; pdb.set_trace()
```

Then attach to container:
```bash
docker attach <container_id>
```

### Database Debugging

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U spotbot_user -d spotbot_db

# View all submissions
SELECT * FROM submissions ORDER BY created_at DESC LIMIT 10;

# View detection results
SELECT * FROM detection_results ORDER BY created_at DESC LIMIT 10;
```

### Redis Debugging

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# View all keys
KEYS *

# Get specific value
GET your_key
```

## Performance Monitoring

### Request Timing

Check `X-Process-Time` header in responses:
```bash
curl -i http://localhost:8000/api/v1/detect/test
```

### Database Query Timing

Check backend logs for SQLAlchemy query times:
```bash
docker-compose logs backend | grep "SQL"
```

## Environment Variables

Create `.env` file in project root:

```env
# Backend
DATABASE_URL=postgresql://spotbot_user:spotbot_password@postgres:5432/spotbot_db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
AI_DETECTOR_URL=http://ai-detector:8001
DEBUG=True

# AI Detector
MODEL_PATH=/app/models

# Frontend
VITE_API_URL=http://localhost:8000
```

## Useful Commands

```bash
# Rebuild specific service
docker-compose up --build backend

# View logs for specific service
docker-compose logs -f ai-detector

# Restart specific service
docker-compose restart backend

# Execute command in running container
docker-compose exec backend python -m pip list

# Clean rebuild everything
docker-compose down -v
docker-compose up --build

# View resource usage
docker stats
```

## VS Code Debugging

Install "Remote - Containers" extension and add `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "attach",
      "connect": {
        "host": "localhost",
        "port": 5678
      },
      "pathMappings": [
        {
          "localRoot": "${workspaceFolder}/backend",
          "remoteRoot": "/app"
        }
      ]
    }
  ]
}
```

## API Testing Tools

### Recommended Tools (Telescope Alternatives for FastAPI)

1. **Swagger UI** (Built-in): http://localhost:8000/docs
2. **ReDoc** (Built-in): http://localhost:8000/redoc
3. **Postman**: Import OpenAPI spec from `/docs`
4. **HTTPie**: CLI tool for API testing
   ```bash
   http POST localhost:8000/api/v1/detect content_type=text content_text="test"
   ```
5. **FastAPI Debugger**: VSCode extension for debugging FastAPI apps

## Monitoring in Production

For production monitoring (Telescope-like functionality):

- **Sentry**: Error tracking and performance monitoring
- **Prometheus + Grafana**: Metrics and dashboards
- **ELK Stack**: Centralized logging
- **New Relic / DataDog**: APM (Application Performance Monitoring)

Add to `requirements.txt`:
```
sentry-sdk[fastapi]==1.40.0
prometheus-fastapi-instrumentator==6.1.0
```
