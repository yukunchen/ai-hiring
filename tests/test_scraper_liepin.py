"""Tests for Liepin scraper."""
import pytest
from app.services.scrapers.liepin import LiepinScraper


# ==================== Scraper Basic Tests ====================


def test_scraper_returns_candidate_list():
    """Test scraper returns candidate list."""
    scraper = LiepinScraper()
    results = scraper._get_mock_results("Python", "北京", 10)

    assert isinstance(results, list)
    assert len(results) > 0


def test_scraper_filter_by_keyword():
    """Test keyword filtering in results."""
    scraper = LiepinScraper()
    results = scraper._get_mock_results("Java", "上海", 5)

    # All results should contain the keyword
    for result in results:
        assert "Java" in result["title"]


def test_scraper_returns_required_fields():
    """Test scraper returns all required fields."""
    scraper = LiepinScraper()
    results = scraper._get_mock_results("Python", "北京", 1)

    required_fields = ["name", "title", "company", "experience", "location", "source", "resume_url"]
    for field in required_fields:
        assert field in results[0]


# ==================== Scraper Configuration Tests ====================


def test_scraper_disabled():
    """Test scraper returns mock data when disabled."""
    scraper = LiepinScraper(cookies="")
    results = scraper._get_mock_results("Python", "北京", 5)

    assert isinstance(results, list)
    assert len(results) == 5


@pytest.mark.asyncio
async def test_scraper_with_empty_cookies():
    """Test scraper with empty cookies."""
    scraper = LiepinScraper(cookies="")
    results = await scraper.search_candidates("Python", "北京", 10)

    # Should return mock data
    assert isinstance(results, list)
    assert len(results) <= 10


# ==================== Scraper Async Tests ====================


@pytest.mark.asyncio
async def test_search_candidates_async():
    """Test async search candidates."""
    scraper = LiepinScraper()
    results = await scraper.search_candidates("Python", "北京", 5)

    assert isinstance(results, list)
    assert len(results) <= 5


@pytest.mark.asyncio
async def test_search_with_location_filter():
    """Test search with location filter."""
    scraper = LiepinScraper()
    results = await scraper.search_candidates("工程师", "深圳", 10)

    for result in results:
        assert result.get("location") == "深圳"


# ==================== Scraper Edge Cases ====================


def test_scraper_empty_keyword():
    """Test scraper with empty keyword returns data."""
    scraper = LiepinScraper()
    results = scraper._get_mock_results("", None, 5)

    # Should still return results
    assert isinstance(results, list)


def test_scraper_limit():
    """Test result limit is respected."""
    scraper = LiepinScraper()
    results = scraper._get_mock_results("Python", "北京", 3)

    assert len(results) == 3


def test_scraper_large_limit():
    """Test large limit returns max 10 mock results."""
    scraper = LiepinScraper()
    results = scraper._get_mock_results("Python", "北京", 100)

    # Mock data max is 10
    assert len(results) == 10
