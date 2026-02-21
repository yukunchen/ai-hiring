"""Tests for Resume service."""
import pytest
from pathlib import Path
from app.services.resume import ResumeService


# ==================== Resume Naming Tests ====================


def test_resume_naming_convention():
    """Test resume filename generation."""
    service = ResumeService()
    filename = service.generate_filename(
        job_id=1,
        candidate_id=100,
        name="张三",
        url="https://example.com/resume.pdf",
    )

    assert filename == "1_100_张三.pdf"


def test_resume_naming_with_special_chars():
    """Test resume naming with special characters in name."""
    service = ResumeService()
    filename = service.generate_filename(
        job_id=1,
        candidate_id=100,
        name="张 三",
        url="https://example.com/resume.pdf",
    )

    # Should sanitize special characters
    assert "张三" in filename
    assert filename.endswith(".pdf")


def test_resume_extension_from_url():
    """Test file extension from URL."""
    service = ResumeService()

    # Test PDF
    filename = service.generate_filename(1, 1, "Test", "https://example.com/resume.pdf")
    assert filename.endswith(".pdf")

    # Test DOCX
    filename = service.generate_filename(1, 1, "Test", "https://example.com/resume.docx")
    assert filename.endswith(".docx")

    # Test DOC
    filename = service.generate_filename(1, 1, "Test", "https://example.com/resume.doc")
    assert filename.endswith(".doc")


# ==================== Directory Tests ====================


def test_resume_storage_directory_creation(tmp_path):
    """Test directory creation."""
    service = ResumeService(storage_dir=str(tmp_path / "resumes" / "new"))

    # Directory should be created
    assert service.storage_dir.exists()


def test_resume_list_empty_directory(tmp_path):
    """Test listing empty directory."""
    service = ResumeService(storage_dir=str(tmp_path))
    resumes = service.list_resumes()

    assert resumes == []


def test_resume_list_with_files(tmp_path):
    """Test listing directory with files."""
    # Create test files
    (tmp_path / "resume1.pdf").write_text("test1")
    (tmp_path / "resume2.pdf").write_text("test2")
    (tmp_path / "note.txt").write_text("test")

    # List resumes - should include files
    resumes = list(tmp_path.iterdir())

    # Should have files
    assert len(resumes) > 0
    assert "resume1.pdf" in resumes
    assert "resume2.pdf" in resumes
    assert "note.txt" not in resumes


# ==================== Resume Path Tests ====================


def test_get_resume_path_exists(tmp_path):
    """Test getting path for existing file."""
    test_file = tmp_path / "test.pdf"
    test_file.write_text("test content")

    service = ResumeService(storage_dir=str(tmp_path))
    path = service.get_resume_path("test.pdf")

    assert path is not None
    assert Path(path).exists()


def test_get_resume_path_not_exists(tmp_path):
    """Test getting path for non-existing file."""
    service = ResumeService(storage_dir=str(tmp_path))
    path = service.get_resume_path("nonexistent.pdf")

    assert path is None


# ==================== Delete Tests ====================


def test_delete_resume_success(tmp_path):
    """Test deleting existing file."""
    test_file = tmp_path / "test.pdf"
    test_file.write_text("test content")

    service = ResumeService(storage_dir=str(tmp_path))
    result = service.delete_resume(str(test_file))

    assert result is True
    assert not test_file.exists()


def test_delete_resume_not_exists(tmp_path):
    """Test deleting non-existing file."""
    service = ResumeService(storage_dir=str(tmp_path))
    result = service.delete_resume(str(tmp_path / "nonexistent.pdf"))

    assert result is False
