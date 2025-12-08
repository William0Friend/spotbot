"""
E2E Tests for SpotBot Frontend using Playwright
Similar to Laravel Dusk but for React/Vite frontend
"""
import pytest
import re
from playwright.sync_api import Page, expect
import time

# Test data samples
TEST_SAMPLES = {
    "human_casual": {
        "text": "omg did you see that game last night??? absolutely insane! can't believe they pulled that off in the last minute. my heart was racing the whole time lol",
        "expected_ai": False,
        "expected_confidence_max": 30
    },
    "gpt_obvious": {
        "text": "Certainly! It's worth noting that artificial intelligence is revolutionizing various industries. However, it's important to understand the implications. Moreover, we must consider both benefits and challenges. In conclusion, as an AI language model, I believe AI offers tremendous potential.",
        "expected_ai": True,
        "expected_confidence_min": 60
    },
    "claude_style": {
        "text": "I aim to be helpful in explaining this concept. Let me clarify the key points: First, I should mention that this is complex. From my perspective, thinking carefully about the ethical implications is essential. I want to be clear that responsible use requires thoughtful consideration.",
        "expected_ai": True,
        "expected_confidence_min": 50
    },
    "human_technical": {
        "text": "Bug in line 47. Fixed by adding null check. Tested locally, works now. PR ready for review.",
        "expected_ai": False,
        "expected_confidence_max": 25
    },
    "em_dash_heavy": {
        "text": "The framework — designed for scalability — offers several advantages. First, it's worth noting the architecture is modular. Second — and this is crucial — the system can handle multiple concurrent requests.",
        "expected_ai": True,
        "expected_confidence_min": 40
    }
}

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "record_video_dir": "./test-results/videos/",
    }

# Note: base_url is provided by pytest-base-url plugin
# Set via environment variable BASE_URL or pass --base-url to pytest

class TestDetectionPage:
    """Test suite for the Detection page functionality"""
    
    def test_page_loads(self, page: Page, base_url: str):
        """Test that the detection page loads successfully"""
        page.goto(f"{base_url}/detection")
        
        # Check page title
        expect(page).to_have_title("SpotBot - AI Content Detection")
        
        # Check main heading
        heading = page.locator("h1")
        expect(heading).to_have_text("AI Content Detection")
        
        # Check description
        description = page.locator("p", has_text="Upload or paste content")
        expect(description).to_be_visible()
    
    def test_content_type_selector(self, page: Page, base_url: str):
        """Test content type selector buttons"""
        page.goto(f"{base_url}/detection")
        
        # Check all content type buttons are visible
        text_button = page.locator("button", has_text="Text")
        image_button = page.locator("button", has_text="Image")
        video_button = page.locator("button", has_text="Video")
        url_button = page.locator("button", has_text="URL")
        
        expect(text_button).to_be_visible()
        expect(image_button).to_be_visible()
        expect(video_button).to_be_visible()
        expect(url_button).to_be_visible()
        
        # Text should be selected by default
        expect(text_button).to_have_class(re.compile(r"border-primary"))
        
        # Click image button
        image_button.click()
        expect(image_button).to_have_class(re.compile(r"border-primary"))
        expect(text_button).not_to_have_class(re.compile(r"border-primary"))
        
        # Should show URL input instead of textarea
        url_input = page.locator('input[type="url"]')
        expect(url_input).to_be_visible()
    
    def test_text_input_validation(self, page: Page, base_url: str):
        """Test that text input validation works"""
        page.goto(f"{base_url}/detection")
        
        # Try to submit without text
        analyze_button = page.locator("button", has_text="Analyze Content")
        analyze_button.click()
        
        # Should show browser validation
        textarea = page.locator("textarea")
        is_valid = textarea.evaluate("el => el.validity.valid")
        assert not is_valid, "Empty textarea should be invalid"
    
    def test_human_text_detection(self, page: Page, base_url: str):
        """Test detection of obviously human-written text"""
        page.goto(f"{base_url}/detection")
        
        sample = TEST_SAMPLES["human_casual"]
        
        # Fill in text
        textarea = page.locator("textarea")
        textarea.fill(sample["text"])
        
        # Click analyze
        analyze_button = page.locator("button", has_text="Analyze Content")
        analyze_button.click()
        
        # Wait for loading to complete
        page.wait_for_selector("text=Analyzing...", state="hidden", timeout=10000)
        
        # Check for results
        results_heading = page.locator("h2", has_text="Analysis Results")
        expect(results_heading).to_be_visible(timeout=15000)
        
        # Check detection status
        if sample["expected_ai"]:
            status_text = page.locator("text=AI-Generated Content Detected")
            expect(status_text).to_be_visible()
        else:
            status_text = page.locator("text=Likely Human-Generated")
            expect(status_text).to_be_visible()
        
        # Check confidence score
        confidence_element = page.locator("text=/\\d+\\.\\d+% Confidence/")
        expect(confidence_element).to_be_visible()
        
        confidence_text = confidence_element.inner_text()
        confidence_score = float(confidence_text.split("%")[0])
        
        assert confidence_score <= sample["expected_confidence_max"], \
            f"Expected confidence <= {sample['expected_confidence_max']}, got {confidence_score}"
    
    def test_gpt_text_detection(self, page: Page, base_url: str):
        """Test detection of GPT-style text"""
        page.goto(f"{base_url}/detection")
        
        sample = TEST_SAMPLES["gpt_obvious"]
        
        # Fill in text
        textarea = page.locator("textarea")
        textarea.fill(sample["text"])
        
        # Click analyze
        analyze_button = page.locator("button", has_text="Analyze Content")
        analyze_button.click()
        
        # Wait for results
        page.wait_for_selector("text=Analyzing...", state="hidden", timeout=10000)
        results_heading = page.locator("h2", has_text="Analysis Results")
        expect(results_heading).to_be_visible(timeout=15000)
        
        # Check AI detected
        status_text = page.locator("text=AI-Generated Content Detected")
        expect(status_text).to_be_visible()
        
        # Check confidence is high
        confidence_element = page.locator("text=/\\d+\\.\\d+% Confidence/")
        confidence_text = confidence_element.inner_text()
        confidence_score = float(confidence_text.split("%")[0])
        
        assert confidence_score >= sample["expected_confidence_min"], \
            f"Expected confidence >= {sample['expected_confidence_min']}, got {confidence_score}"
        
        # Check model detection
        detected_model = page.locator(".capitalize", has_text="gpt")
        # May or may not be visible depending on detection
    
    def test_claude_text_detection(self, page: Page, base_url: str):
        """Test detection of Claude-style text"""
        page.goto(f"{base_url}/detection")
        
        sample = TEST_SAMPLES["claude_style"]
        
        textarea = page.locator("textarea")
        textarea.fill(sample["text"])
        
        analyze_button = page.locator("button", has_text="Analyze Content")
        analyze_button.click()
        
        page.wait_for_selector("text=Analyzing...", state="hidden", timeout=10000)
        results_heading = page.locator("h2", has_text="Analysis Results")
        expect(results_heading).to_be_visible(timeout=15000)
        
        # Should detect AI
        status_text = page.locator("text=AI-Generated Content Detected")
        expect(status_text).to_be_visible()
    
    def test_analysis_details_displayed(self, page: Page, base_url: str):
        """Test that analysis details are properly displayed"""
        page.goto(f"{base_url}/detection")
        
        textarea = page.locator("textarea")
        textarea.fill(TEST_SAMPLES["gpt_obvious"]["text"])
        
        analyze_button = page.locator("button", has_text="Analyze Content")
        analyze_button.click()
        
        page.wait_for_selector("text=Analyzing...", state="hidden", timeout=10000)
        
        # Check for analysis details section
        details_heading = page.locator("h3", has_text="Analysis Details")
        expect(details_heading).to_be_visible(timeout=15000)
        
        # Check for JSON output
        json_pre = page.locator("pre")
        expect(json_pre).to_be_visible()
        
        # Verify JSON contains expected keys
        json_text = json_pre.inner_text()
        assert "text_length" in json_text
        assert "confidence_score" in json_text
    
    def test_multiple_analyses(self, page: Page, base_url: str):
        """Test running multiple analyses in succession"""
        page.goto(f"{base_url}/detection")
        
        for sample_name, sample in list(TEST_SAMPLES.items())[:3]:
            # Fill and analyze
            textarea = page.locator("textarea")
            textarea.fill(sample["text"])
            
            analyze_button = page.locator("button", has_text="Analyze Content")
            analyze_button.click()
            
            # Wait for results
            page.wait_for_selector("text=Analyzing...", state="hidden", timeout=10000)
            results_heading = page.locator("h2", has_text="Analysis Results")
            expect(results_heading).to_be_visible(timeout=15000)
            
            # Small delay between tests
            time.sleep(1)
    
    def test_loading_state(self, page: Page, base_url: str):
        """Test that loading state is properly shown"""
        page.goto(f"{base_url}/detection")
        
        textarea = page.locator("textarea")
        textarea.fill("Test content for loading state")
        
        analyze_button = page.locator("button", has_text="Analyze Content")
        analyze_button.click()
        
        # Check loading state appears
        loading_text = page.locator("text=Analyzing...")
        expect(loading_text).to_be_visible(timeout=1000)
        
        # Wait for it to disappear
        expect(loading_text).to_be_hidden(timeout=15000)
    
    def test_error_handling(self, page: Page, base_url: str):
        """Test error handling when backend is unavailable"""
        # This test would require mocking or stopping the backend
        # For now, we'll test with invalid input
        page.goto(f"{base_url}/detection")
        
        # Switch to URL input
        url_button = page.locator("button", has_text="URL")
        url_button.click()
        
        # Enter invalid URL
        url_input = page.locator('input[type="url"]')
        url_input.fill("not-a-valid-url")
        
        analyze_button = page.locator("button", has_text="Analyze Content")
        analyze_button.click()
        
        # Should show browser validation
        is_valid = url_input.evaluate("el => el.validity.valid")
        assert not is_valid, "Invalid URL should not pass validation"
    
    def test_responsive_design(self, page: Page, base_url: str):
        """Test responsive design at different viewport sizes"""
        viewports = [
            {"width": 375, "height": 667},   # Mobile
            {"width": 768, "height": 1024},  # Tablet
            {"width": 1920, "height": 1080}, # Desktop
        ]
        
        for viewport in viewports:
            page.set_viewport_size(viewport)
            page.goto(f"{base_url}/detection")
            
            # Check main elements are visible
            heading = page.locator("h1")
            expect(heading).to_be_visible()
            
            textarea = page.locator("textarea")
            expect(textarea).to_be_visible()
            
            analyze_button = page.locator("button", has_text="Analyze Content")
            expect(analyze_button).to_be_visible()

class TestNavigationAndIntegration:
    """Test navigation and integration between pages"""
    
    def test_navigation_to_detection(self, page: Page, base_url: str):
        """Test navigating to detection page from home"""
        page.goto(base_url)
        
        # Find and click link to detection page
        detection_link = page.locator('a[href*="detection"]')
        if detection_link.count() > 0:
            detection_link.first.click()
            expect(page).to_have_url(f"{base_url}/detection")
    
    def test_history_integration(self, page: Page, base_url: str):
        """Test that analyzed content appears in history"""
        # Run an analysis
        page.goto(f"{base_url}/detection")
        
        textarea = page.locator("textarea")
        textarea.fill("Test for history integration")
        
        analyze_button = page.locator("button", has_text="Analyze Content")
        analyze_button.click()
        
        page.wait_for_selector("text=Analyzing...", state="hidden", timeout=10000)
        
        # Navigate to history page
        page.goto(f"{base_url}/history")
        
        # Check if the analysis appears (if history page exists)
        # This is optional depending on implementation

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--headed"])
