"""
Application Configuration Manager

Handles loading and validation of environment variables
for AI, database, and application settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env file from backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # AI Configuration (LM Studio)
    ai_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="Base URL for LM Studio local server"
    )
    ai_api_key: str = Field(
        default="lm-studio",
        description="API key for LM Studio"
    )
    ai_model: str = Field(
        default="local-model",
        description="Model name for AI inference"
    )

    # Database Configuration (SQL Server)
    db_server: str = Field(
        default="localhost",
        description="SQL Server instance name"
    )
    db_name: str = Field(
        default="GB_TIMAH_DATA",
        description="Database name"
    )
    db_user: str = Field(
        default="",
        description="SQL Authentication username"
    )
    db_password: str = Field(
        default="",
        description="SQL Authentication password"
    )
    db_use_windows_auth: bool = Field(
        default=True,
        description="Use Windows Authentication instead of SQL Auth"
    )

    # Application Settings
    data_folder: str = Field(
        default="./data",
        description="Path to data folder containing Excel/CSV files"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    # Server Settings
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")

    @property
    def db_connection_string(self) -> str:
        """Generate ODBC connection string for SQL Server."""
        if self.db_use_windows_auth:
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.db_server};"
                f"DATABASE={self.db_name};"
                f"Trusted_Connection=yes;"
            )
        else:
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.db_server};"
                f"DATABASE={self.db_name};"
                f"UID={self.db_user};"
                f"PWD={self.db_password};"
            )

    @property
    def data_path(self) -> Path:
        """Get resolved data folder path."""
        return Path(self.data_folder).resolve()

    def validate_data_folder(self) -> None:
        """Ensure data folder exists, create if missing."""
        if not self.data_path.exists():
            self.data_path.mkdir(parents=True, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
settings.validate_data_folder()