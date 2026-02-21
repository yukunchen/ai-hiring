"""Scraper factory for managing multiple recruitment websites."""
from typing import Optional
from app.services.scrapers.liepin import LiepinScraper
from app.services.scrapers.zhipin import ZhipinScraper
from app.services.scrapers.linkedin import LinkedInScraper


class ScraperFactory:
    """Factory for creating and managing scrapers."""

    SCRAPERS = {
        "liepin": LiepinScraper,
        "zhipin": ZhipinScraper,
        "linkedin": LinkedInScraper,
    }

    def __init__(self):
        """Initialize scraper factory."""
        self._scrapers = {}

    def get_scraper(self, name: str, cookies: Optional[str] = None):
        """Get scraper by name.

        Args:
            name: Scraper name (liepin, zhipin, linkedin)
            cookies: Optional cookies

        Returns:
            Scraper instance
        """
        if name not in self.SCRAPERS:
            raise ValueError(f"Unknown scraper: {name}")

        if name not in self._scrapers:
            self._scrapers[name] = self.SCRAPERS[name](cookies=cookies)

        return self._scrapers[name]

    def get_all_scrapers(self):
        """Get all available scrapers.

        Returns:
            Dict of scraper name to instance
        """
        return {
            name: self.get_scraper(name)
            for name in self.SCRAPERS
        }

    def search_all(
        self,
        keyword: str,
        location: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Search all enabled scrapers.

        Args:
            keyword: Search keyword
            location: Filter by location
            limit: Results per scraper

        Returns:
            Combined list of results
        """
        results = []
        for name, scraper in self.get_all_scrapers().items():
            try:
                scraper_results = scraper.search_candidates(keyword, location, limit)
                results.extend(scraper_results)
            except Exception:
                pass
        return results

    @property
    def available_sources(self) -> list[str]:
        """Get list of available sources."""
        return list(self.SCRAPERS.keys())


# Singleton instance
_scraper_factory = None


def get_scraper_factory() -> ScraperFactory:
    """Get singleton scraper factory."""
    global _scraper_factory
    if _scraper_factory is None:
        _scraper_factory = ScraperFactory()
    return _scraper_factory
