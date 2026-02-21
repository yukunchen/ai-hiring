"""Configuration management for AI Hiring System."""
import os
from pathlib import Path
from typing import Optional
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get project root (parent of app directory)
PROJECT_ROOT = Path(__file__).parent.parent


class Config:
    """Application configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_path: Path to config file. Defaults to config.yaml in project root.
        """
        self.config_path = config_path or str(PROJECT_ROOT / "config.yaml")
        self._config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # Replace environment variables
        return self._replace_env_vars(config)

    def _replace_env_vars(self, config: dict) -> dict:
        """Replace ${VAR} patterns with environment variables."""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            return os.getenv(env_var, "")
        return config

    @property
    def database_path(self) -> str:
        """Get database path."""
        db_path = self._config.get("database", {}).get("path", "aihiring.db")
        return str(PROJECT_ROOT / db_path)

    @property
    def resume_dir(self) -> str:
        """Get resume storage directory."""
        resume_dir = self._config.get("storage", {}).get("resume_dir", "resumes")
        return str(PROJECT_ROOT / resume_dir)

    @property
    def openai_api_key(self) -> str:
        """Get OpenAI API key."""
        return self._config.get("openai", {}).get("api_key", "")

    @property
    def openai_model(self) -> str:
        """Get OpenAI model."""
        return self._config.get("openai", {}).get("model", "gpt-4")

    @property
    def scrapers(self) -> dict:
        """Get scraper configuration."""
        return self._config.get("scrapers", {})

    @property
    def smtp(self) -> dict:
        """Get SMTP configuration."""
        return self._config.get("smtp", {})

    @property
    def app(self) -> dict:
        """Get app configuration."""
        return self._config.get("app", {})


# Global config instance
config = Config()
