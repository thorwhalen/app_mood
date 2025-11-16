"""Playwright E2E test configuration."""
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
    }


@pytest.fixture
def base_url():
    """Base URL for the application."""
    return "http://localhost:3000"


@pytest.fixture
def api_url():
    """API URL for backend calls."""
    return "http://localhost:8000/api/v1"


def wait_for_services(base_url: str, api_url: str, timeout: int = 60):
    """Wait for frontend and backend services to be ready."""
    import requests
    from time import sleep, time as current_time

    start_time = current_time()

    while current_time() - start_time < timeout:
        try:
            # Check backend health
            requests.get(f"{api_url.replace('/api/v1', '')}/health", timeout=5)
            # Check frontend
            requests.get(base_url, timeout=5)
            print("Services are ready!")
            return True
        except requests.RequestException:
            print("Waiting for services to start...")
            sleep(2)

    raise TimeoutError("Services did not start within timeout period")


@pytest.fixture(scope="session", autouse=True)
def setup_services(base_url, api_url):
    """Ensure services are running before tests."""
    wait_for_services(base_url, api_url)
