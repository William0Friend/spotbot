#!/bin/bash

# SpotBot AI Detection Test Suite
# This script tests the enhanced AI detection system with various text samples

echo "🤖 SpotBot AI Detection Test Suite"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test function
test_detection() {
    local name="$1"
    local text="$2"
    local expected_result="$3"
    
    echo -e "${BLUE}Test: $name${NC}"
    echo "Text: ${text:0:100}..."
    echo ""
    
    response=$(curl -s -X POST http://localhost:8001/analyze \
      -H "Content-Type: application/json" \
      -d "{\"content_type\":\"text\",\"content_text\":\"$text\"}")
    
    confidence=$(echo "$response" | jq -r '.confidence_score')
    label=$(echo "$response" | jq -r '.confidence_label')
    model=$(echo "$response" | jq -r '.detected_model')
    is_ai=$(echo "$response" | jq -r '.is_ai_generated')
    
    echo "Results:"
    echo "  Confidence: $confidence% ($label)"
    echo "  Detected Model: $model"
    echo "  Is AI: $is_ai"
    
    # Check if result matches expectation
    if [ "$is_ai" == "$expected_result" ]; then
        echo -e "  ${GREEN}✓ PASS${NC}"
    else
        echo -e "  ${RED}✗ FAIL (expected: $expected_result, got: $is_ai)${NC}"
    fi
    
    echo ""
    echo "---"
    echo ""
}

echo "Waiting for services to be ready..."
sleep 3

echo -e "${YELLOW}=== Test 1: Your Original Text ===${NC}"
test_detection \
  "User's Original Text (Should be LOW)" \
  "Nice idea — high-impact and hard in all the right ways. I'll lay out a practical, citation-backed plan you can build from: what the product is, how detection/attribution actually works today (and its limits), a concrete system architecture (MVP → production), data & tooling choices, legal/privacy concerns, evaluation, and a suggested 90-day roadmap. I'll call the product SpotBot in examples." \
  "false"

echo -e "${YELLOW}=== Test 2: Obvious ChatGPT Text ===${NC}"
test_detection \
  "ChatGPT Style (Should be HIGH)" \
  "Certainly! It's worth noting that artificial intelligence is revolutionizing various industries. However, it's important to understand the implications of these advancements. Moreover, we must consider both the benefits and challenges associated with AI implementation. In conclusion, as an AI language model, I believe that while AI offers tremendous potential, it's crucial to approach its development responsibly." \
  "true"

echo -e "${YELLOW}=== Test 3: Claude-like Text ===${NC}"
test_detection \
  "Claude Style (Should be MODERATE-HIGH)" \
  "I aim to be helpful in explaining this concept. Let me clarify the key points: First, I should mention that this is a complex topic. From my perspective, thinking carefully about the ethical implications is essential. I want to be clear that responsible use of this technology requires thoughtful consideration of all stakeholders involved." \
  "true"

echo -e "${YELLOW}=== Test 4: Human Blog Post ===${NC}"
test_detection \
  "Human Writing (Should be LOW)" \
  "So I just tried this new coffee shop downtown. Honestly? Pretty disappointing. The barista seemed confused by my order and the espresso tasted burnt. Not sure I'll go back. Has anyone else been there? Let me know your thoughts!" \
  "false"

echo -e "${YELLOW}=== Test 5: Academic AI Text ===${NC}"
test_detection \
  "Academic AI Style (Should be HIGH)" \
  "Research suggests that climate change represents one of the most significant challenges facing humanity. It is important to note that multiple factors contribute to this phenomenon. Furthermore, according to scientific consensus, urgent action is required. In summary, while solutions exist, it is crucial that governments and individuals take immediate steps to address this global issue." \
  "true"

echo -e "${YELLOW}=== Test 6: Casual Human Text ===${NC}"
test_detection \
  "Casual Human (Should be LOW)" \
  "omg did you see that game last night??? absolutely insane! can't believe they pulled that off in the last minute. my heart was racing the whole time lol. definitely going to watch the replay" \
  "false"

echo -e "${YELLOW}=== Test 7: Em Dash Heavy (GPT Signature) ===${NC}"
test_detection \
  "GPT Em Dash Style (Should be MODERATE)" \
  "The framework — designed for scalability — offers several advantages. First, it's worth noting the architecture is modular. Second — and this is crucial — the system can handle multiple concurrent requests. Moreover, the documentation is comprehensive, making it easy to get started." \
  "true"

echo -e "${YELLOW}=== Test 8: Short Technical Human ===${NC}"
test_detection \
  "Short Technical (Should be LOW)" \
  "Bug in line 47. Fixed by adding null check. Tested locally, works now. PR ready for review." \
  "false"

echo ""
echo -e "${GREEN}Test Suite Complete!${NC}"
echo ""
echo "📊 View detailed analysis at: http://localhost:8000/docs"
echo "🔍 Check logs: docker-compose logs -f ai-detector"
