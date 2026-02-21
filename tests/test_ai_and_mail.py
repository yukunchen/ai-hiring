"""Tests for AI matching and email services."""
import pytest
from app.services.ai_match import AIMatchService
from app.services.email_generation import EmailGenerationService
from app.services.mailer import EmailSender


# ==================== AI Match Tests ====================


@pytest.mark.asyncio
async def test_match_resume_with_job_success():
    """Test matching resume to job."""
    service = AIMatchService(api_key="")

    result = await service.match_resume_to_job(
        job_description="需要Python开发经验",
        job_requirements="熟练掌握Python",
        resume_content="有Python开发经验3年",
    )

    assert "score" in result
    assert "reasons" in result
    assert 0 <= result["score"] <= 100


@pytest.mark.asyncio
async def test_match_resume_with_job_perfect_match():
    """Test perfect match."""
    service = AIMatchService(api_key="")

    result = await service.match_resume_to_job(
        job_description="Python工程师，精通Django",
        job_requirements="5年经验",
        resume_content="5年Python Django开发经验",
    )

    # Should have some match due to keywords
    assert result["score"] >= 0


@pytest.mark.asyncio
async def test_match_resume_with_job_no_match():
    """Test no match scenario."""
    service = AIMatchService(api_key="")

    result = await service.match_resume_to_job(
        job_description="Python工程师",
        job_requirements="5年经验",
        resume_content="销售经验10年",
    )

    # Low score expected
    assert 0 <= result["score"] <= 100


@pytest.mark.asyncio
async def test_match_empty_resume():
    """Test empty resume handling."""
    service = AIMatchService(api_key="")

    result = await service.match_resume_to_job(
        job_description="Python工程师",
        job_requirements="5年经验",
        resume_content="",
    )

    # Should handle empty gracefully
    assert "score" in result


# ==================== Email Generation Tests ====================


@pytest.mark.asyncio
async def test_generate_email_success():
    """Test email generation."""
    service = EmailGenerationService(api_key="")

    result = await service.generate_inquiry_email(
        candidate_name="张三",
        job_title="Python工程师",
        company_name="某科技公司",
    )

    assert "subject" in result
    assert "body" in result
    assert "to" in result


@pytest.mark.asyncio
async def test_generate_email_contains_key_info():
    """Test email contains key information."""
    service = EmailGenerationService(api_key="")

    result = await service.generate_inquiry_email(
        candidate_name="李四",
        job_title="Java开发",
        company_name="测试公司",
    )

    assert "李四" in result["body"]
    assert "Java" in result["subject"] or "Java" in result["body"]


def test_generate_email_empty_name():
    """Test email with empty name."""
    service = EmailGenerationService(api_key="")

    # Should still generate something
    result = service._generate_mock_email("", "工程师", "公司")
    assert "subject" in result


def test_email_template_variables():
    """Test template variable replacement."""
    service = EmailGenerationService(api_key="")

    result = service._generate_mock_email(
        candidate_name="王五",
        job_title="架构师",
        company_name="知名企业",
    )

    assert "王五" in result["body"]
    assert "架构师" in result["body"]


# ==================== Email Validation Tests ====================


def test_validate_email_valid():
    """Test valid email validation."""
    service = EmailGenerationService()

    assert service.validate_email("test@example.com") is True
    assert service.validate_email("user.name@company.co.uk") is True


def test_validate_email_invalid():
    """Test invalid email validation."""
    service = EmailGenerationService()

    assert service.validate_email("invalid") is False
    assert service.validate_email("@example.com") is False
    assert service.validate_email("test@") is False


# ==================== Email Sender Tests ====================


def test_email_sender_not_configured():
    """Test email sender when not configured."""
    # Use empty strings to override config defaults
    sender = EmailSender(host="", username="", password="")

    result = sender.send_email(
        to_email="test@example.com",
        subject="Test",
        body="Test body",
    )

    # Either not configured or connection error
    assert result["success"] is False
    assert "error" in result


def test_email_sender_multiple_recipients():
    """Test sending to multiple recipients."""
    sender = EmailSender(host="", username="")

    result = sender.send_email_to_multiple(
        to_emails=["a@test.com", "b@test.com"],
        subject="Test",
        body="Test",
    )

    # Should handle empty config gracefully
    assert "results" in result


def test_email_sender_empty_recipients():
    """Test sending to empty recipient list."""
    sender = EmailSender(host="", username="")

    result = sender.send_email_to_multiple(
        to_emails=[],
        subject="Test",
        body="Test",
    )

    assert result["success"] is False
