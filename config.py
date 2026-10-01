import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Base configuration settings for TaskFlow."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-taskflow-2026")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'taskflow.db'}"
    )

class DevelopmentConfig(Config):
    """Configuration for local development."""
    DEBUG = True

class TestingConfig(Config):
    """Configuration for automated test suite."""
    TESTING = True
    DEBUG = False
    # Use fast in-memory SQLite database for test isolation
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(Config):
    """Configuration for production deployment."""
    DEBUG = False

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
