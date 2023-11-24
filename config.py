import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
	"""Base configuration."""

	SQLALCHEMY_DATABASE_URI = os.getenv(
		"DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'travel_library.db')}"
	)
	# Default secret key
	SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")

	# Default SQLAlchemy settings
	# SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///travel_library.db")
	SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
	"""Development configuration."""

	DEBUG = True
	SQLALCHEMY_ECHO = True  # If you want to see SQLAlchemy queries in the logs


class TestingConfig(Config):
	"""Testing configuration."""

	TESTING = True
	SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # Use in-memory SQLite for tests


class ProductionConfig(Config):
	"""Production configuration."""

	DEBUG = False
