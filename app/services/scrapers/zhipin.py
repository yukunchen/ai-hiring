"""BOSS Zhipin scraper service."""
from typing import Optional
import httpx

from app.config import config


class ZhipinScraper:
    """BOSS Zhipin recruitment website scraper."""

    def __init__(self, cookies: Optional[str] = None):
        """Initialize scraper.

        Args:
            cookies: Authenticated cookies for BOSS
        """
        self.cookies = cookies or config.scrapers.get("zhipin", {}).get("cookies", "")
        self.base_url = config.scrapers.get("zhipin", {}).get("base_url", "https://www.zhipin.com")
        self.enabled = config.scrapers.get("zhipin", {}).get("enabled", True)

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
        # Real implementation would use httpx to send authenticated requests
        # Parse HTML with BeautifulSoup
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
            f"高级{keyword}工程师",
            f"{keyword}开发",
            f"{keyword}专家",
            f"资深{keyword}",
            f"{keyword}负责人",
        ]
        companies = [
            "美团",
            "拼多多",
            "京东",
            "滴滴",
            "快手",
            "小红书",
            "蔚来",
            "理想汽车",
        ]
        locations = location and [location] or ["北京", "上海", "深圳", "杭州", "广州"]
        experiences = ["1年", "2年", "3年", "5年", "8年"]

        for i in range(min(limit, 10)):
            mock_candidates.append({
                "name": f"Boss候选人{i+1}",
                "title": titles[i % len(titles)],
                "company": companies[i % len(companies)],
                "experience": experiences[i % len(experiences)],
                "location": locations[i % len(locations)],
                "source": "zhipin",
                "source_url": f"https://www.zhipin.com/web/geek/job?pid={10000+i}",
                "resume_url": f"https://www.zhipin.com/resume/download/{10000+i}.pdf",
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


def get_scraper() -> ZhipinScraper:
    """Get singleton scraper instance."""
    return ZhipinScraper()
