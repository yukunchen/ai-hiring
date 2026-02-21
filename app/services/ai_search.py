"""AI-powered search service with matching."""
from typing import Optional
from app.services.scrapers.factory import get_scraper_factory
from app.services.ai_match import get_ai_match_service


class AISearchService:
    """AI-powered candidate search and matching service."""

    def __init__(self):
        """Initialize AI search service."""
        self.scraper_factory = get_scraper_factory()
        self.ai_match = get_ai_match_service()

    async def search_with_ai_match(
        self,
        job_id: int,
        job_title: str,
        job_description: str,
        job_requirements: str,
        keyword: str,
        location: Optional[str] = None,
        sources: list[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Search candidates and rank by AI match score.

        Args:
            job_id: Job ID
            job_title: Job title
            job_description: Job description
            job_requirements: Job requirements
            keyword: Search keyword
            location: Filter by location
            sources: List of sources to search
            limit: Maximum results

        Returns:
            List of candidates with match scores
        """
        # Default sources
        if sources is None:
            sources = ["liepin", "zhipin", "linkedin"]

        # Search from all sources
        all_candidates = []
        for source in sources:
            try:
                scraper = self.scraper_factory.get_scraper(source)
                candidates = await scraper.search_candidates(
                    keyword=keyword,
                    location=location,
                    limit=limit,
                )
                for c in candidates:
                    c["source"] = source
                all_candidates.extend(candidates)
            except Exception:
                pass

        # Calculate match scores for each candidate
        results = []
        for candidate in all_candidates:
            try:
                # Build resume content from candidate info
                resume_content = self._build_resume_text(candidate)

                # Check if AI client is available
                if self.ai_match.client:
                    # Get AI match
                    match_result = await self.ai_match.match_resume_to_job(
                        job_description=job_description,
                        job_requirements=job_requirements,
                        resume_content=resume_content,
                    )
                    candidate["match_score"] = match_result.get("score", 0)
                    candidate["match_reasons"] = match_result.get("reasons", [])
                else:
                    # Use keyword-based matching
                    match_result = self._keyword_match(
                        job_title=job_title,
                        job_description=job_description,
                        job_requirements=job_requirements,
                        candidate=candidate,
                    )
                    candidate["match_score"] = match_result.get("score", 0)
                    candidate["match_reasons"] = match_result.get("reasons", [])

                results.append(candidate)
            except Exception:
                candidate["match_score"] = 0
                candidate["match_reasons"] = []
                results.append(candidate)

        # Sort by match score (descending)
        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)

        return results[:limit]

    def _keyword_match(
        self,
        job_title: str,
        job_description: str,
        job_requirements: str,
        candidate: dict,
    ) -> dict:
        """Simple keyword-based matching without AI."""
        # Build job text
        job_text = f"{job_title} {job_description} {job_requirements}".lower()

        # Build candidate text
        candidate_text = f"{candidate.get('title', '')} {candidate.get('company', '')} {candidate.get('experience', '')}".lower()

        # Simple keyword matching - check for common terms
        # Extract potential keywords (English words and Chinese keywords)
        import re
        job_words = set(re.findall(r'[a-z]+', job_text))
        candidate_words = set(re.findall(r'[a-z]+', candidate_text))

        # Also check Chinese (simplified - check if job keywords appear in candidate)
        score = 0
        matched_terms = []

        # English keyword matching
        common_english = job_words & candidate_words
        if common_english:
            score += len(common_english) * 30
            matched_terms.extend(list(common_english))

        # Check if job title appears in candidate title
        if job_title.lower() in candidate.get('title', '').lower():
            score += 30
            matched_terms.append(job_title)

        # Check if key terms match
        key_terms = ['python', 'java', '工程师', '开发', '架构', 'manager', 'engineer', 'developer']
        for term in key_terms:
            if term in job_text and term in candidate_text:
                score += 15
                if term not in matched_terms:
                    matched_terms.append(term)

        # Cap score at 100
        score = min(100, score)

        reasons = []
        if score >= 80:
            reasons.append("关键词高度匹配")
        elif score >= 50:
            reasons.append("有一定关键词匹配")
        else:
            reasons.append("关键词匹配较少")

        if matched_terms:
            reasons.append(f"匹配: {', '.join(matched_terms[:3])}")

        return {"score": score, "reasons": reasons}

    def _build_resume_text(self, candidate: dict) -> str:
        """Build resume text from candidate info."""
        parts = []
        if candidate.get("name"):
            parts.append(f"姓名: {candidate['name']}")
        if candidate.get("title"):
            parts.append(f"职位: {candidate['title']}")
        if candidate.get("company"):
            parts.append(f"公司: {candidate['company']}")
        if candidate.get("experience"):
            parts.append(f"经验: {candidate['experience']}")
        if candidate.get("location"):
            parts.append(f"地点: {candidate['location']}")
        return "\n".join(parts) if parts else "无"


# Singleton instance
_ai_search_service = None


def get_ai_search_service() -> AISearchService:
    """Get singleton AI search service."""
    global _ai_search_service
    if _ai_search_service is None:
        _ai_search_service = AISearchService()
    return _ai_search_service
