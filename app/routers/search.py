"""Search API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.services.scrapers.liepin import get_scraper

router = APIRouter(prefix="/api/search", tags=["Search"])


class SearchRequest(BaseModel):
    """Search request model."""

    keyword: str
    job_id: int
    location: Optional[str] = None
    limit: int = 20


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
        scraper = get_scraper()
        results = await scraper.search_candidates(
            keyword=request.keyword,
            location=request.location,
            limit=request.limit,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("")
async def search_candidates_get(
    keyword: str = Query(..., min_length=1),
    job_id: int = Query(..., gt=0),
    location: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
):
    """Search candidates (GET method).

    Args:
        keyword: Search keyword
        job_id: Job ID to associate candidates with
        location: Filter by location
        limit: Maximum results

    Returns:
        List of candidate results
    """
    try:
        scraper = get_scraper()
        results = await scraper.search_candidates(
            keyword=keyword,
            location=location,
            limit=limit,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
