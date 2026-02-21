"""Search API routes for multi-source candidate search."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.services.scrapers.factory import get_scraper_factory

router = APIRouter(prefix="/api/search", tags=["Search"])


class SearchRequest(BaseModel):
    """Search request model."""

    keyword: str
    job_id: int
    location: Optional[str] = None
    limit: int = 20
    sources: Optional[List[str]] = None  # Specify which sources to search


class CandidateResult(BaseModel):
    """Candidate search result model."""

    name: str
    title: Optional[str]
    company: Optional[str]
    experience: Optional[str]
    location: Optional[str]
    source: str
    source_url: Optional[str]
    resume_url: Optional[str]


@router.post("")
async def search_candidates(
    request: SearchRequest,
):
    """Search candidates from recruitment websites.

    Args:
        request: Search request with keyword and filters

    Returns:
        List of candidate results
    """
    try:
        factory = get_scraper_factory()

        # Determine sources to search
        sources = request.sources or ["liepin", "zhipin", "linkedin"]
        all_results = []

        for source in sources:
            try:
                scraper = factory.get_scraper(source)
                results = await scraper.search_candidates(
                    keyword=request.keyword,
                    location=request.location,
                    limit=request.limit,
                )
                all_results.extend(results)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
            except Exception:
                pass

        return all_results[:request.limit * len(sources)]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("")
async def search_candidates_get(
    keyword: str = Query(..., min_length=1),
    job_id: int = Query(..., gt=0),
    location: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    sources: Optional[str] = Query(None, description="Comma-separated sources: liepin,zhipin,linkedin"),
):
    """Search candidates (GET method).

    Args:
        keyword: Search keyword
        job_id: Job ID to associate candidates with
        location: Filter by location
        limit: Maximum results
        sources: Comma-separated list of sources

    Returns:
        List of candidate results
    """
    try:
        factory = get_scraper_factory()

        # Parse sources
        source_list = sources.split(",") if sources else ["liepin", "zhipin", "linkedin"]
        all_results = []

        for source in source_list:
            source = source.strip()
            try:
                scraper = factory.get_scraper(source)
                results = await scraper.search_candidates(
                    keyword=keyword,
                    location=location,
                    limit=limit,
                )
                all_results.extend(results)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unknown source: {source}")
            except Exception:
                pass

        return all_results[:limit * len(source_list)]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/sources")
async def get_available_sources():
    """Get list of available search sources.

    Returns:
        List of available sources
    """
    factory = get_scraper_factory()
    return {
        "sources": factory.available_sources,
    }


@router.get("/sources/{source}")
async def get_source_status(source: str):
    """Get status of a specific source.

    Args:
        source: Source name

    Returns:
        Source status
    """
    factory = get_scraper_factory()

    try:
        scraper = factory.get_scraper(source)
        return {
            "source": source,
            "enabled": getattr(scraper, "enabled", True),
            "has_cookies": bool(getattr(scraper, "cookies", "")),
        }
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown source: {source}")
