"""Candidate management API routes."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field, EmailStr

from app.database import get_db
from app.models import Candidate
from app.services.resume_generation import get_resume_generation_service

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

# Valid statuses
VALID_STATUSES = ["pending", "contacted", "interviewing", "offered", "hired", "rejected"]


# Pydantic schemas
class CandidateCreate(BaseModel):
    """Schema for creating a candidate."""

    job_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    source: str = Field(default="liepin")
    source_url: Optional[str] = None
    resume_path: Optional[str] = None
    resume_content: Optional[str] = None
    match_score: Optional[int] = Field(None, ge=0, le=100)
    status: str = Field(default="pending")
    notes: Optional[str] = None


class CandidateUpdate(BaseModel):
    """Schema for updating a candidate."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    source_url: Optional[str] = None
    resume_path: Optional[str] = None
    resume_content: Optional[str] = None
    match_score: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    notes: Optional[str] = None


class CandidateResponse(BaseModel):
    """Schema for candidate response."""

    id: int
    job_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    title: Optional[str]
    company: Optional[str]
    experience: Optional[str]
    education: Optional[str]
    source: str
    source_url: Optional[str]
    resume_path: Optional[str]
    resume_content: Optional[str]
    match_score: Optional[int]
    status: str
    notes: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new candidate.

    Args:
        candidate_data: Candidate creation data
        db: Database session

    Returns:
        Created candidate
    """
    # Validate status
    if candidate_data.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Must be one of: {VALID_STATUSES}",
        )

    candidate = Candidate(**candidate_data.model_dump())
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)
    return candidate.to_dict()


@router.get("", response_model=List[CandidateResponse])
async def list_candidates(
    skip: int = 0,
    limit: int = 100,
    job_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List all candidates.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        job_id: Filter by job ID
        status: Filter by status
        db: Database session

    Returns:
        List of candidates
    """
    query = select(Candidate)
    if job_id:
        query = query.where(Candidate.job_id == job_id)
    if status:
        query = query.where(Candidate.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    candidates = result.scalars().all()
    return [c.to_dict() for c in candidates]


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a candidate by ID.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        Candidate details

    Raises:
        HTTPException: If candidate not found
    """
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate.to_dict()


@router.patch("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a candidate.

    Args:
        candidate_id: Candidate ID
        candidate_data: Candidate update data
        db: Database session

    Returns:
        Updated candidate

    Raises:
        HTTPException: If candidate not found or invalid status
    """
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Validate status if provided
    update_data = candidate_data.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] not in VALID_STATUSES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status. Must be one of: {VALID_STATUSES}",
        )

    for field, value in update_data.items():
        setattr(candidate, field, value)

    await db.commit()
    await db.refresh(candidate)
    return candidate.to_dict()


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete a candidate.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Raises:
        HTTPException: If candidate not found
    """
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    await db.delete(candidate)
    await db.commit()


@router.post("/{candidate_id}/generate-resume", response_model=CandidateResponse)
async def generate_candidate_resume(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Generate AI resume for a candidate based on their basic info.

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        Updated candidate with generated resume content

    Raises:
        HTTPException: If candidate not found
    """
    result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Generate resume using AI service
    resume_service = get_resume_generation_service()
    resume_content = await resume_service.generate_resume_from_info(
        name=candidate.name,
        title=candidate.title,
        company=candidate.company,
        experience=candidate.experience,
        source=candidate.source,
    )

    # Update candidate with generated resume
    candidate.resume_content = resume_content
    await db.commit()
    await db.refresh(candidate)

    return candidate.to_dict()
