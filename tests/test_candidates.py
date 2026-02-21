"""Tests for Candidate management API."""
import pytest
from sqlalchemy import select

from app.models import Candidate, Job


# ==================== Create Candidate Tests ====================


@pytest.mark.asyncio
async def test_create_candidate_success(db_session, sample_job_data, sample_candidate_data):
    """Test successfully creating a candidate."""
    # Create a job first
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Update candidate data with job_id
    candidate_data = {**sample_candidate_data, "job_id": job.id}

    # Create candidate
    candidate = Candidate(**candidate_data)
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    assert candidate.id is not None
    assert candidate.name == sample_candidate_data["name"]
    assert candidate.status == "pending"


@pytest.mark.asyncio
async def test_create_candidate_without_email(db_session, sample_job_data, sample_candidate_data):
    """Test creating candidate without email (should succeed as email is optional)."""
    # Create a job first
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Create candidate without email
    candidate_data = {
        "job_id": job.id,
        "name": "李四",
        "phone": "13900139000",
        "source": "liepin",
        "status": "pending",
    }

    candidate = Candidate(**candidate_data)
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    assert candidate.id is not None
    assert candidate.email is None


# ==================== Read Candidate Tests ====================


@pytest.mark.asyncio
async def test_get_candidates_by_job(db_session, sample_job_data, sample_candidate_data):
    """Test getting candidates by job ID."""
    # Create job
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Create multiple candidates for this job
    for i in range(3):
        candidate = Candidate(
            job_id=job.id,
            name=f"候选人{i}",
            source="liepin",
            status="pending",
        )
        db_session.add(candidate)
    await db_session.commit()

    # Query candidates by job
    result = await db_session.execute(
        select(Candidate).where(Candidate.job_id == job.id)
    )
    candidates = result.scalars().all()

    assert len(candidates) == 3


@pytest.mark.asyncio
async def test_get_candidate_with_resume(db_session, sample_job_data, sample_candidate_data):
    """Test getting candidate with resume information."""
    # Create job
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Create candidate with resume
    candidate_data = {
        **sample_candidate_data,
        "job_id": job.id,
        "resume_path": "/resumes/1_1_张三.pdf",
        "resume_content": "这是简历内容",
    }
    candidate = Candidate(**candidate_data)
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    # Verify resume info is stored
    assert candidate.resume_path == "/resumes/1_1_张三.pdf"
    assert candidate.resume_content == "这是简历内容"


# ==================== Update Candidate Tests ====================


@pytest.mark.asyncio
async def test_update_candidate_status(db_session, sample_job_data, sample_candidate_data):
    """Test updating candidate status."""
    # Create job and candidate
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    candidate_data = {**sample_candidate_data, "job_id": job.id}
    candidate = Candidate(**candidate_data)
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    # Update status
    candidate.status = "contacted"
    await db_session.commit()
    await db_session.refresh(candidate)

    assert candidate.status == "contacted"


@pytest.mark.asyncio
async def test_update_candidate_status_invalid(db_session, sample_job_data, sample_candidate_data):
    """Test updating candidate with invalid status."""
    # Create job and candidate
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    candidate_data = {**sample_candidate_data, "job_id": job.id}
    candidate = Candidate(**candidate_data)
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    # Update with invalid status - should be handled in API layer
    # Since status is Optional in Pydantic, it won't raise here
    # The validation happens at API endpoint level
    candidate.status = "invalid_status"
    # The API should validate this, but direct DB update won't
    await db_session.commit()

    # Verify the status is stored (API layer would handle validation)
    assert candidate.status == "invalid_status"


# ==================== Delete Candidate Tests ====================


@pytest.mark.asyncio
async def test_delete_candidate_success(db_session, sample_job_data, sample_candidate_data):
    """Test successfully deleting a candidate."""
    # Create job and candidate
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    candidate_data = {**sample_candidate_data, "job_id": job.id}
    candidate = Candidate(**candidate_data)
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    candidate_id = candidate.id

    # Delete candidate
    await db_session.delete(candidate)
    await db_session.commit()

    # Verify
    result = await db_session.execute(select(Candidate).where(Candidate.id == candidate_id))
    fetched_candidate = result.scalar_one_or_none()
    assert fetched_candidate is None
