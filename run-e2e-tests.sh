#!/bin/bash
# SpotBot Test Setup and Execution Script

set -e

echo "🧪 SpotBot E2E Test Setup"
echo "=========================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
echo -e "\n${YELLOW}1. Checking if services are running...${NC}"
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${RED}❌ Services not running. Starting services...${NC}"
    docker-compose up -d
    echo -e "${YELLOW}⏳ Waiting 30 seconds for services to start...${NC}"
    sleep 30
else
    echo -e "${GREEN}✓ Services are running${NC}"
fi

# Check frontend availability
echo -e "\n${YELLOW}2. Checking frontend availability...${NC}"
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo -e "${GREEN}✓ Frontend is available${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}⏳ Waiting for frontend... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Frontend not available after $MAX_RETRIES retries${NC}"
    exit 1
fi

# Check backend availability
echo -e "\n${YELLOW}3. Checking backend availability...${NC}"
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✓ Backend is available${NC}"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo -e "${YELLOW}⏳ Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)${NC}"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo -e "${RED}❌ Backend not available after $MAX_RETRIES retries${NC}"
    exit 1
fi

# Install test dependencies
echo -e "\n${YELLOW}4. Installing test dependencies...${NC}"
if [ ! -d "tests/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv tests/venv
fi

source tests/venv/bin/activate
pip install -q --upgrade pip
pip install -q -r tests/requirements.txt

# Install Playwright browsers
echo -e "\n${YELLOW}5. Installing Playwright browsers...${NC}"
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    playwright install chromium
    echo -e "${GREEN}✓ Playwright browsers installed${NC}"
else
    echo -e "${GREEN}✓ Playwright browsers already installed${NC}"
fi

# Create test results directory
mkdir -p test-results/videos
mkdir -p test-results/screenshots

# Run tests
echo -e "\n${YELLOW}6. Running E2E tests...${NC}"
echo "================================"

# Export environment variables for tests
export BASE_URL="http://localhost:3000"
export API_URL="http://localhost:8000"
export HEADLESS="${HEADLESS:-true}"
export SLOW_MO="${SLOW_MO:-0}"
export RECORD_VIDEO="${RECORD_VIDEO:-false}"

# Run pytest with verbose output
pytest tests/e2e/test_detection_page.py -v \
    --base-url="http://localhost:3000" \
    --tb=short \
    --color=yes \
    --capture=no \
    "$@"

TEST_EXIT_CODE=$?

echo -e "\n================================"
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo -e "${YELLOW}Check test-results/ directory for screenshots and videos${NC}"
fi

echo -e "\n${YELLOW}Test artifacts saved to:${NC}"
echo "  - Screenshots: test-results/screenshots/"
echo "  - Videos: test-results/videos/"

deactivate

exit $TEST_EXIT_CODE
