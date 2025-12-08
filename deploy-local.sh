#!/bin/bash
# Quick deployment script for SpotBot

set -e

echo "🚀 SpotBot Deployment Script"
echo "============================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << 'EOF'
# Database
POSTGRES_USER=spotbot_user
POSTGRES_PASSWORD=change_this_password
POSTGRES_DB=spotbot_db

# Redis
REDIS_PASSWORD=change_this_redis_password

# Backend
SECRET_KEY=change_this_to_random_secret_key
JWT_SECRET=change_this_to_random_jwt_secret
DATABASE_URL=postgresql://spotbot_user:change_this_password@postgres:5432/spotbot_db
REDIS_URL=redis://:change_this_redis_password@redis:6379/0

# Frontend
VITE_API_URL=http://localhost:8000
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and change the passwords!${NC}"
    echo ""
fi

# Build and start services
echo -e "${BLUE}Building and starting services...${NC}"
docker-compose down
docker-compose up --build -d

echo ""
echo -e "${BLUE}Waiting for services to be healthy...${NC}"
sleep 10

# Check service health
echo ""
echo -e "${BLUE}Checking service status:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}Checking backend health...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ Backend is healthy${NC}"
        break
    fi
    echo -e "${YELLOW}Waiting for backend... ($i/30)${NC}"
    sleep 2
done

echo ""
echo -e "${BLUE}Checking frontend...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✓ Frontend is healthy${NC}"
        break
    fi
    echo -e "${YELLOW}Waiting for frontend... ($i/30)${NC}"
    sleep 2
done

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✓ SpotBot is ready!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔍 Test detection:"
echo '   curl -X POST http://localhost:8000/api/v1/detect/ \'
echo '     -H "Content-Type: application/json" \'
echo '     -d '"'"'{"content_type": "text", "content_text": "Your text here"}'"'"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f backend"
echo "   docker-compose logs -f frontend"
echo "   docker-compose logs -f ai-detector"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
