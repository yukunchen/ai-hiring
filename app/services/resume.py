"""Resume download and management service."""
import os
from pathlib import Path
from typing import Optional
import httpx
from urllib.parse import urlparse

from app.config import config


class ResumeService:
    """Resume download and management service."""

    def __init__(self, storage_dir: Optional[str] = None):
        """Initialize resume service.

        Args:
            storage_dir: Directory to store resumes
        """
        self.storage_dir = Path(storage_dir or config.resume_dir)
        self._ensure_storage_dir()

    def _ensure_storage_dir(self):
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def generate_filename(
        self,
        job_id: int,
        candidate_id: int,
        name: str,
        url: str,
    ) -> str:
        """Generate resume filename.

        Args:
            job_id: Job ID
            candidate_id: Candidate ID
            name: Candidate name
            url: Resume URL

        Returns:
            Generated filename
        """
        # Get file extension from URL
        parsed = urlparse(url)
        path = parsed.path
        ext = os.path.splitext(path)[1] if "." in path else ".pdf"

        # Sanitize name for filename
        safe_name = "".join(c for c in name if c.isalnum() or c in "-_")

        return f"{job_id}_{candidate_id}_{safe_name}{ext}"

    async def download_resume(
        self,
        url: str,
        job_id: int,
        candidate_id: int,
        name: str,
        cookies: Optional[str] = None,
    ) -> Optional[str]:
        """Download resume from URL.

        Args:
            url: Resume URL
            job_id: Job ID
            candidate_id: Candidate ID
            name: Candidate name
            cookies: Optional cookies for authentication

        Returns:
            Path to downloaded file, or None on failure
        """
        if not url:
            return None

        try:
            # Generate filename
            filename = self.generate_filename(job_id, candidate_id, name, url)
            filepath = self.storage_dir / filename

            # Download file
            async with httpx.AsyncClient() as client:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                response = await client.get(url, headers=headers, timeout=30.0)

                if response.status_code == 200:
                    # Write to file
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    return str(filepath)

        except Exception as e:
            print(f"Failed to download resume: {e}")

        return None

    def get_resume_path(self, filename: str) -> Optional[str]:
        """Get full path to resume file.

        Args:
            filename: Resume filename

        Returns:
            Full path to file, or None if not found
        """
        filepath = self.storage_dir / filename
        if filepath.exists():
            return str(filepath)
        return None

    def delete_resume(self, filepath: str) -> bool:
        """Delete resume file.

        Args:
            filepath: Full path to resume file

        Returns:
            True if deleted, False otherwise
        """
        try:
            path = Path(filepath)
            if path.exists() and path.is_file():
                path.unlink()
                return True
        except Exception:
            pass
        return False

    def list_resumes(self) -> list[str]:
        """List all resume files.

        Returns:
            List of resume filenames
        """
        if not self.storage_dir.exists():
            return []
        return [f.name for f in self.storage_dir.iterdir() if f.is_file()]


# Singleton instance
_resume_service = None


def get_resume_service() -> ResumeService:
    """Get singleton resume service instance."""
    global _resume_service
    if _resume_service is None:
        _resume_service = ResumeService()
    return _resume_service
