"""
Unit tests for configuration module.
"""

import pytest
from pydantic import ValidationError

from backend.core.config import (
    AppSettings,
    DatabaseSettings,
    RedisSettings,
    SecuritySettings,
)


class TestDatabaseSettings:
    """Tests for DatabaseSettings."""
    
    def test_default_values(self):
        """Test default values are set correctly."""
        settings = DatabaseSettings()
        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.name == "atlas"
        assert settings.user == "atlas"
    
    def test_get_url(self):
        """Test URL generation."""
        settings = DatabaseSettings(
            host="testhost",
            port=5433,
            name="testdb",
            user="testuser",
            password="testpass",
        )
        url = settings.get_url()
        assert "postgresql+asyncpg://" in url
        assert "testuser" in url
        assert "testpass" in url
        assert "testhost" in url
        assert "5433" in url
        assert "testdb" in url
    
    def test_custom_url_overrides_components(self):
        """Test that custom URL overrides component values."""
        custom_url = "postgresql+asyncpg://custom:pass@customhost:5434/customdb"
        settings = DatabaseSettings(url=custom_url)
        assert settings.get_url() == custom_url


class TestRedisSettings:
    """Tests for RedisSettings."""
    
    def test_default_values(self):
        """Test default values are set correctly."""
        settings = RedisSettings()
        assert settings.host == "localhost"
        assert settings.port == 6379
        assert settings.db == 0
        assert settings.ssl is False
        assert settings.decode_responses is True
    
    def test_get_url_without_password(self):
        """Test URL generation without password."""
        settings = RedisSettings(
            host="redishost",
            port=6380,
            db=2,
        )
        url = settings.get_url()
        assert "redis://" in url
        assert "redishost" in url
        assert "6380" in url
        assert "2" in url
    
    def test_get_url_with_password(self):
        """Test URL generation with password."""
        settings = RedisSettings(
            host="redishost",
            port=6380,
            db=2,
            password="secret",
        )
        url = settings.get_url()
        assert "redis://:secret@" in url


class TestSecuritySettings:
    """Tests for SecuritySettings."""
    
    def test_default_values(self):
        """Test default values are set correctly."""
        settings = SecuritySettings()
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30
        assert settings.refresh_token_expire_days == 7
        assert settings.password_min_length == 8
        assert settings.password_require_uppercase is True
        assert settings.password_require_lowercase is True
        assert settings.password_require_digit is True
        assert settings.password_require_special is False


class TestAppSettings:
    """Tests for AppSettings."""
    
    def test_default_values(self):
        """Test default values are set correctly."""
        settings = AppSettings()
        assert settings.name == "ATLAS Platform"
        assert settings.version == "1.0.1"
        assert settings.debug is False
        assert settings.environment == "development"
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
    
    def test_cors_origins_string_parsing(self):
        """Test CORS origins string parsing."""
        settings = AppSettings(cors_origins='["http://localhost:3000", "http://localhost:8000"]')
        assert len(settings.cors_origins) == 2
        assert "http://localhost:3000" in settings.cors_origins
    
    def test_cors_origins_list(self):
        """Test CORS origins list passthrough."""
        origins = ["http://example.com", "https://app.example.com"]
        settings = AppSettings(cors_origins=origins)
        assert settings.cors_origins == origins
