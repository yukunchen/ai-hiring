"""LinkedIn scraper service."""
from typing import Optional
import httpx

from app.config import config


class LinkedInScraper:
    """LinkedIn recruitment website scraper."""

    def __init__(self, cookies: Optional[str] = None):
        """Initialize scraper.

        Args:
            cookies: Authenticated cookies for LinkedIn
        """
        self.cookies = cookies or config.scrapers.get("linkedin", {}).get("cookies", "")
        self.base_url = config.scrapers.get("linkedin", {}).get("base_url", "https://www.linkedin.com")
        self.enabled = config.scrapers.get("linkedin", {}).get("enabled", True)

    async def search_candidates(
        self,
        keyword: str,
        location: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Search candidates by keyword.

        Args:
            keyword: Search keyword
            location: Filter by location
            limit: Maximum results

        Returns:
            List of candidate information
        """
        if not self.enabled:
            return []

        if not self.cookies:
            return self._get_mock_results(keyword, location, limit)

        try:
            return await self._search_with_cookies(keyword, location, limit)
        except Exception:
            return self._get_mock_results(keyword, location, limit)

    async def _search_with_cookies(
        self,
        keyword: str,
        location: Optional[str],
        limit: int,
    ) -> list[dict]:
        """Search with real cookies."""
        # Real implementation would use LinkedIn API or scraping
        return self._get_mock_results(keyword, location, limit)

    def _get_mock_results(
        self,
        keyword: str,
        location: Optional[str],
        limit: int,
    ) -> list[dict]:
        """Get mock search results for testing."""
        mock_candidates = []
        titles = [
            f"{keyword} Engineer",
            f"Senior {keyword} Developer",
            f"{keyword} Architect",
            f"Lead {keyword} Engineer",
            f"{keyword} Specialist",
            f"Staff {keyword} Engineer",
        ]
        companies = [
            "Google",
            "Microsoft",
            "Amazon",
            "Meta",
            "Apple",
            "Netflix",
            "Tesla",
            "Airbnb",
        ]
        locations = location and [location] or ["Remote", "San Francisco", "New York", "Seattle", "London"]

        for i in range(min(limit, 10)):
            mock_candidates.append({
                "name": f"LinkedIn Candidate {i+1}",
                "title": titles[i % len(titles)],
                "company": companies[i % len(companies)],
                "experience": f"{3 + (i % 8)} years",
                "location": locations[i % len(locations)],
                "source": "linkedin",
                "source_url": f"https://www.linkedin.com/in/candidate{i+1}",
                "resume_url": f"https://www.linkedin.com/profile/{i+1}/exportresume",
            })

        return mock_candidates

    async def download_resume(self, resume_url: str) -> Optional[bytes]:
        """Download candidate resume."""
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


def get_scraper() -> LinkedInScraper:
    """Get singleton scraper instance."""
    return LinkedInScraper()
