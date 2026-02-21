"""Tests for BOSS Zhipin scraper."""
import pytest
from app.services.scrapers.zhipin import ZhipinScraper


def test_zhipin_scraper_returns_candidates():
    """Test scraper returns candidate list."""
    scraper = ZhipinScraper()
    results = scraper._get_mock_results("Python", "北京", 5)

    assert isinstance(results, list)
    assert len(results) == 5
    assert all(r["source"] == "zhipin" for r in results)


def test_zhipin_scraper_keyword():
    """Test scraper uses keyword."""
    scraper = ZhipinScraper()
    results = scraper._get_mock_results("Java", "上海", 3)

    assert len(results) == 3
    for r in results:
        assert "Java" in r["title"]


def test_zhipin_scraper_required_fields():
    """Test scraper returns required fields."""
    scraper = ZhipinScraper()
    results = scraper._get_mock_results("Python", "北京", 1)

    required = ["name", "title", "company", "experience", "location", "source", "resume_url"]
    for field in required:
        assert field in results[0]


@pytest.mark.asyncio
async def test_zhipin_search_async():
    """Test async search."""
    scraper = ZhipinScraper()
    results = await scraper.search_candidates("Python", "北京", 5)

    assert isinstance(results, list)
    assert len(results) <= 5


def test_zhipin_scraper_disabled():
    """Test disabled scraper."""
    scraper = ZhipinScraper()
    scraper.enabled = False

    results = scraper._get_mock_results("Python", "北京", 5)
    # Mock data still works
    assert len(results) == 5
