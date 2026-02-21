"""Liepin scraper service."""
import os
from typing import Optional
import httpx
from bs4 import BeautifulSoup

from app.config import config


class LiepinScraper:
    """Liepin recruitment website scraper."""

    def __init__(self, cookies: Optional[str] = None):
        """Initialize scraper.

        Args:
            cookies: Authenticated cookies for Liepin
        """
        self.cookies = cookies or config.scrapers.get("liepin", {}).get("cookies", "")
        self.base_url = config.scrapers.get("liepin", {}).get("base_url", "https://www.liepin.com")
        self.enabled = config.scrapers.get("liepin", {}).get("enabled", True)

    async def search_candidates(
        self,
        keyword: str,
        location: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Search candidates by keyword.

        Args:
            keyword: Search keyword (job title, skill, etc.)
            location: Filter by location
            limit: Maximum number of results

        Returns:
            List of candidate information dictionaries
        """
        if not self.enabled:
            return self._get_mock_results(keyword, location, limit)

        # If no cookies, use mock data
        if not self.cookies:
            return self._get_mock_results(keyword, location, limit)

        try:
            return await self._search_with_cookies(keyword, location, limit)
        except Exception as e:
            # Fall back to mock data on error
            return self._get_mock_results(keyword, location, limit)

    async def _search_with_cookies(
        self,
        keyword: str,
        location: Optional[str],
        limit: int,
    ) -> list[dict]:
        """Search with real cookies (placeholder for real implementation)."""
        # Real implementation would:
        # 1. Use httpx to send authenticated request
        # 2. Parse HTML response with BeautifulSoup
        # 3. Extract candidate info

        # For now, return mock data
        return self._get_mock_results(keyword, location, limit)

    def _get_mock_results(
        self,
        keyword: str,
        location: Optional[str],
        limit: int,
    ) -> list[dict]:
        """Get mock search results for testing.

        Args:
            keyword: Search keyword
            location: Filter by location
            limit: Maximum number of results

        Returns:
            List of mock candidate data
        """
        # Generate mock candidates based on keyword
        mock_candidates = []
        titles = [
            f"高级{keyword}工程师",
            f"{keyword}开发工程师",
            f"{keyword}架构师",
            f"资深{keyword}",
            f"{keyword}技术专家",
        ]

        companies = [
            "字节跳动",
            "阿里巴巴",
            "腾讯",
            "美团",
            "拼多多",
            "京东",
            "网易",
            "快手",
        ]

        experiences = ["1-3年", "3-5年", "5-10年", "10年以上"]

        for i in range(min(limit, 10)):
            mock_candidates.append({
                "name": f"候选人{i+1}",
                "title": titles[i % len(titles)],
                "company": companies[i % len(companies)],
                "experience": experiences[i % len(experiences)],
                "location": location or "北京",
                "source": "liepin",
                "source_url": f"https://www.liepin.com/candidate/{1000+i}",
                "resume_url": f"https://www.liepin.com/resume/{1000+i}.pdf",
            })

        return mock_candidates

    async def download_resume(self, resume_url: str) -> Optional[bytes]:
        """Download candidate resume.

        Args:
            resume_url: URL of the resume

        Returns:
            Resume file content as bytes, or None on failure
        """
        if not self.cookies:
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    resume_url,
                    cookies=self._parse_cookies(),
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.content
        except Exception:
            pass

        return None

    def _parse_cookies(self) -> dict:
        """Parse cookies string to dictionary."""
        cookies = {}
        if self.cookies:
            for part in self.cookies.split(";"):
                if "=" in part:
                    key, value = part.strip().split("=", 1)
                    cookies[key] = value
        return cookies


# Singleton instance
_scraper = None


def get_scraper() -> LiepinScraper:
    """Get singleton scraper instance."""
    global _scraper
    if _scraper is None:
        _scraper = LiepinScraper()
    return _scraper
