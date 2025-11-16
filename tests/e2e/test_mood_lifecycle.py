"""E2E tests for mood lifecycle using Playwright."""
import pytest
from playwright.sync_api import Page, expect


def test_create_mood_user_story(page: Page, base_url: str):
    """
    User Story 1: Create a new mood definition
    - Navigate to create mood page
    - Fill in mood attributes
    - Submit and verify creation
    - Verify mood appears in list
    """
    # Navigate to moods page
    page.goto(base_url)
    page.click('text=Moods')

    # Click create mood button
    page.click('text=Create Mood')

    # Fill in the form
    page.fill('input[name="name"]', 'Test Bullish Sentiment')
    page.fill('textarea[name="description"]', 'Measures optimistic market outlook')
    page.fill(
        'textarea[name="attribute_definition"]',
        'Text expressing positive expectations about future market performance'
    )

    # Submit the form
    page.click('text=Create')

    # Wait for dialog to close and mood to appear
    expect(page.locator('text=Test Bullish Sentiment')).to_be_visible()

    # Verify mood appears in the list
    mood_card = page.locator('text=Test Bullish Sentiment').locator('..')
    expect(mood_card).to_contain_text('Measures optimistic market outlook')


def test_navigate_to_mood_detail(page: Page, base_url: str):
    """
    User Story: Navigate to mood detail page
    - Click on a mood from the list
    - View mood details, datasets, and models
    """
    page.goto(f"{base_url}/moods")

    # If there are moods, click on the first one
    view_details = page.locator('text=View Details').first
    if view_details.is_visible():
        view_details.click()

        # Should see tabs for Datasets and Models
        expect(page.locator('text=Datasets')).to_be_visible()
        expect(page.locator('text=Models')).to_be_visible()


def test_homepage_navigation(page: Page, base_url: str):
    """Test that homepage loads and navigation works."""
    page.goto(base_url)

    # Check that the main heading is visible
    expect(page.locator('text=Welcome to Mood')).to_be_visible()

    # Check navigation items
    expect(page.locator('text=Home')).to_be_visible()
    expect(page.locator('text=Moods')).to_be_visible()
    expect(page.locator('text=Analysis')).to_be_visible()
    expect(page.locator('text=Headlines')).to_be_visible()
    expect(page.locator('text=History')).to_be_visible()


def test_analysis_page_loads(page: Page, base_url: str):
    """Test that analysis page loads correctly."""
    page.goto(f"{base_url}/analysis")

    expect(page.locator('text=Text Analysis')).to_be_visible()
    expect(page.locator('text=Select Mood')).to_be_visible()


def test_headlines_page_loads(page: Page, base_url: str):
    """Test that headlines page loads correctly."""
    page.goto(f"{base_url}/headlines")

    expect(page.locator('text=Financial Headlines')).to_be_visible()


def test_history_page_loads(page: Page, base_url: str):
    """Test that history page loads correctly."""
    page.goto(f"{base_url}/history")

    expect(page.locator('text=Analysis History')).to_be_visible()
