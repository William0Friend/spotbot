#!/bin/bash

# SpotBot Setup Script
# One-command setup for new developers

set -e

echo "🤖 SpotBot Setup Wizard"
echo "======================="
echo ""

# Check dependencies
echo "Checking dependencies..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
else
    echo "✅ Docker found: $(docker --version)"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
else
    echo "✅ Docker Compose found: $(docker-compose --version)"
fi

echo ""

# Setup environment
echo "Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env file"
else
    echo "⚠️  .env file already exists, skipping"
fi

echo ""

# Ask if user wants to start services
read -p "Do you want to start all services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting SpotBot services..."
    echo "This may take a few minutes on first run..."
    echo ""
    
    docker-compose up --build -d
    
    echo ""
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    echo ""
    echo "Checking service health..."
    
    # Check backend
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
    else
        echo "⚠️  Backend might still be starting..."
    fi
    
    # Check AI detector
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ AI Detector is healthy"
    else
        echo "⚠️  AI Detector might still be starting..."
    fi
    
    # Check frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is healthy"
    else
        echo "⚠️  Frontend might still be starting..."
    fi
    
    echo ""
    echo "🎉 SpotBot is running!"
    echo ""
    echo "📍 Access points:"
    echo "   Frontend:    http://localhost:3000"
    echo "   Backend API: http://localhost:8000/docs"
    echo "   AI Detector: http://localhost:8001/docs"
    echo ""
    echo "📝 Useful commands:"
    echo "   View logs:        docker-compose logs -f"
    echo "   Stop services:    docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo "   Run tests:        ./test.sh"
    echo ""
    echo "📚 Documentation:"
    echo "   Quick Start:  QUICKSTART.md"
    echo "   Architecture: ARCHITECTURE.md"
    echo "   Contributing: CONTRIBUTING.md"
    echo ""
    
    # Ask if user wants to open browser
    read -p "Open frontend in browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:3000
        elif command -v open &> /dev/null; then
            open http://localhost:3000
        else
            echo "Please open http://localhost:3000 in your browser"
        fi
    fi
else
    echo ""
    echo "Setup complete! To start services later, run:"
    echo "  docker-compose up --build"
    echo ""
fi

echo ""
echo "Happy coding! 🚀"
