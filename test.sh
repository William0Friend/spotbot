#!/bin/bash

# SpotBot Test Script
# Tests all major functionality of the platform

set -e

echo "🤖 SpotBot Test Suite"
echo "===================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URLs
BACKEND_URL="http://localhost:8000"
AI_DETECTOR_URL="http://localhost:8001"
FRONTEND_URL="http://localhost:3000"

# Test counter
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $response)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC} (Expected HTTP $expected_code, got $response)"
        ((FAILED++))
    fi
}

# Function to test JSON API
test_json_api() {
    local name=$1
    local url=$2
    local method=$3
    local data=$4
    local expected_field=$5
    
    echo -n "Testing $name... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s "$url")
    fi
    
    if echo "$response" | grep -q "$expected_field"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "Response: $response"
        ((FAILED++))
    fi
}

echo "1. Testing Service Health"
echo "-------------------------"
test_endpoint "Backend Health" "$BACKEND_URL/health"
test_endpoint "AI Detector Health" "$AI_DETECTOR_URL/health"
test_endpoint "Frontend" "$FRONTEND_URL" 200
echo ""

echo "2. Testing Backend API"
echo "---------------------"
test_endpoint "API Root" "$BACKEND_URL/"
test_endpoint "API Docs" "$BACKEND_URL/docs"
echo ""

echo "3. Testing AI Detection"
echo "----------------------"

# Test text detection
TEXT_DATA='{
  "content_type": "text",
  "content_text": "As an AI language model, I cannot provide personal opinions. However, I can help you understand this topic. It is important to note that this is a complex subject."
}'

test_json_api "Text AI Detection" "$BACKEND_URL/api/v1/detect/" "POST" "$TEXT_DATA" "confidence_score"

# Test image detection
IMAGE_DATA='{
  "content_type": "image",
  "content_url": "https://via.placeholder.com/512x512"
}'

test_json_api "Image AI Detection" "$BACKEND_URL/api/v1/detect/" "POST" "$IMAGE_DATA" "confidence_score"
echo ""

echo "4. Testing User Authentication"
echo "-----------------------------"

# Generate random username and email
RANDOM_USER="testuser_$(date +%s)"
RANDOM_EMAIL="test_$(date +%s)@example.com"

# Test user registration
REGISTER_DATA='{
  "email": "'$RANDOM_EMAIL'",
  "username": "'$RANDOM_USER'",
  "password": "testpassword123"
}'

test_json_api "User Registration" "$BACKEND_URL/api/v1/auth/register" "POST" "$REGISTER_DATA" "email"

# Test user login
LOGIN_DATA='{
  "email": "'$RANDOM_EMAIL'",
  "password": "testpassword123"
}'

test_json_api "User Login" "$BACKEND_URL/api/v1/auth/login" "POST" "$LOGIN_DATA" "access_token"
echo ""

echo "5. Testing Submissions"
echo "---------------------"
test_json_api "Get Submissions" "$BACKEND_URL/api/v1/submissions/" "GET" "" "[]"
echo ""

# Summary
echo "===================="
echo "📊 Test Summary"
echo "===================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
