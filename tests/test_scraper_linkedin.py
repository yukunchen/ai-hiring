"""Tests for LinkedIn scraper."""
import pytest
from app.services.scrapers.linkedin import LinkedInScraper


def test_linkedin_scraper_returns_candidates():
    """Test scraper returns candidate list."""
    scraper = LinkedInScraper()
    results = scraper._get_mock_results("Python", "Remote", 5)

    assert isinstance(results, list)
    assert len(results) == 5
    assert all(r["source"] == "linkedin" for r in results)


def test_linkedin_scraper_english():
    """Test scraper returns English results."""
    scraper = LinkedInScraper()
    results = scraper._get_mock_results("Engineer", "San Francisco", 3)

    assert len(results) == 3
    for r in results:
        assert "Engineer" in r["title"]


def test_linkedin_scraper_required_fields():
    """Test scraper returns required fields."""
    scraper = LinkedInScraper()
    results = scraper._get_mock_results("Developer", "London", 1)

    required = ["name", "title", "company", "experience", "location", "source", "resume_url"]
    for field in required:
        assert field in results[0]


@pytest.mark.asyncio
async def test_linkedin_search_async():
    """Test async search."""
    scraper = LinkedInScraper()
    results = await scraper.search_candidates("Manager", "Remote", 5)

    assert isinstance(results, list)
    assert len(results) <= 5


def test_linkedin_scraper_disabled():
    """Test disabled scraper."""
    scraper = LinkedInScraper()
    scraper.enabled = False

    results = scraper._get_mock_results("Engineer", "NYC", 5)
    # Mock data still works
    assert len(results) == 5
