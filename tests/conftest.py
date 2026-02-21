"""Pytest configuration and fixtures."""
import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test database path
TEST_DB_PATH = ":memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    from app.database import Base

    engine = create_async_engine(f"sqlite+aiosqlite:///{TEST_DB_PATH}", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncTestSession = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with AsyncTestSession() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def sample_job_data() -> dict:
    """Sample job data for testing."""
    return {
        "title": "Python 工程师",
        "department": "研发部",
        "location": "北京",
        "salary_min": 20000,
        "salary_max": 40000,
        "description": "负责后端服务开发",
        "requirements": "3年以上Python开发经验",
        "status": "open",
    }


@pytest.fixture
def sample_candidate_data() -> dict:
    """Sample candidate data for testing."""
    return {
        "job_id": 1,
        "name": "张三",
        "email": "zhangsan@example.com",
        "phone": "13800138000",
        "title": "高级Python工程师",
        "company": "某互联网公司",
        "experience": "5年",
        "source": "liepin",
        "status": "pending",
    }
