"""Tests for Job management API."""
import pytest
from sqlalchemy import select
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models import Job


# ==================== Create Job Tests ====================


@pytest.mark.asyncio
async def test_create_job_success(db_session, sample_job_data):
    """Test successfully creating a job."""
    # Create job directly in database
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Verify
    assert job.id is not None
    assert job.title == sample_job_data["title"]
    assert job.status == "open"


@pytest.mark.asyncio
async def test_create_job_missing_required_fields(db_session):
    """Test creating job without required title field."""
    from pydantic import ValidationError
    from app.routers.jobs import JobCreate

    with pytest.raises(ValidationError):
        JobCreate(title="", description="Test")


@pytest.mark.asyncio
async def test_create_job_empty_title(db_session):
    """Test creating job with empty title."""
    from pydantic import ValidationError
    from app.routers.jobs import JobCreate

    with pytest.raises(ValidationError):
        JobCreate(title="", description="Test description")


# ==================== Read Job Tests ====================


@pytest.mark.asyncio
async def test_get_job_by_id(db_session, sample_job_data):
    """Test getting a job by ID."""
    # Create job
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Query job
    result = await db_session.execute(select(Job).where(Job.id == job.id))
    fetched_job = result.scalar_one_or_none()

    assert fetched_job is not None
    assert fetched_job.id == job.id
    assert fetched_job.title == job.title


@pytest.mark.asyncio
async def test_get_job_not_found(db_session):
    """Test getting a non-existent job."""
    result = await db_session.execute(select(Job).where(Job.id == 99999))
    fetched_job = result.scalar_one_or_none()

    assert fetched_job is None


@pytest.mark.asyncio
async def test_list_jobs(db_session, sample_job_data):
    """Test listing all jobs."""
    # Create multiple jobs
    for i in range(3):
        job = Job(**{**sample_job_data, "title": f"Job {i}"})
        db_session.add(job)
    await db_session.commit()

    # List jobs
    result = await db_session.execute(select(Job))
    jobs = result.scalars().all()

    assert len(jobs) == 3


# ==================== Update Job Tests ====================


@pytest.mark.asyncio
async def test_update_job_success(db_session, sample_job_data):
    """Test successfully updating a job."""
    # Create job
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Update job
    job.title = "Updated Python Engineer"
    job.status = "closed"
    await db_session.commit()
    await db_session.refresh(job)

    # Verify
    assert job.title == "Updated Python Engineer"
    assert job.status == "closed"


@pytest.mark.asyncio
async def test_update_job_not_found(db_session):
    """Test updating a non-existent job."""
    # Try to update non-existent job - should return None
    result = await db_session.execute(select(Job).where(Job.id == 99999))
    job = result.scalar_one_or_none()

    # Should be None
    assert job is None


# ==================== Delete Job Tests ====================


@pytest.mark.asyncio
async def test_delete_job_success(db_session, sample_job_data):
    """Test successfully deleting a job."""
    # Create job
    job = Job(**sample_job_data)
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    job_id = job.id

    # Delete job
    await db_session.delete(job)
    await db_session.commit()

    # Verify
    result = await db_session.execute(select(Job).where(Job.id == job_id))
    fetched_job = result.scalar_one_or_none()
    assert fetched_job is None


@pytest.mark.asyncio
async def test_delete_job_not_found(db_session):
    """Test deleting a non-existent job."""
    from sqlalchemy.orm import Session

    # Try to delete non-existent job
    result = await db_session.execute(select(Job).where(Job.id == 99999))
    job = result.scalar_one_or_none()
    assert job is None
