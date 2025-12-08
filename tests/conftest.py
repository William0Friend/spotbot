"""
pytest configuration for SpotBot E2E tests
"""
import pytest
from playwright.sync_api import sync_playwright
import os

@pytest.fixture(scope="session")
def playwright():
    """Session-scoped Playwright instance"""
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright):
    """Session-scoped browser instance"""
    browser = playwright.chromium.launch(
        headless=os.getenv("HEADLESS", "true").lower() == "true",
        slow_mo=int(os.getenv("SLOW_MO", "0"))
    )
    yield browser
    browser.close()

@pytest.fixture(scope="function")
def context(browser):
    """Function-scoped browser context"""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir="./test-results/videos/" if os.getenv("RECORD_VIDEO") else None,
    )
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context):
    """Function-scoped page"""
    page = context.new_page()
    yield page
    page.close()
