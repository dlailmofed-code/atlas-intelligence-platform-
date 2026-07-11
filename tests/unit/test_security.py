"""
Unit tests for security module.
"""

from datetime import timedelta

import pytest

from backend.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    validate_password,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "test_password123"
        hashed = hash_password(password)
        assert isinstance(hashed, str)
    
    def test_hash_password_different_from_original(self):
        """Test that hashed password is different from original."""
        password = "test_password123"
        hashed = hash_password(password)
        assert hashed != password
    
    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password."""
        password = "test_password123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for incorrect password."""
        password = "test_password123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False
    
    def test_different_passwords_produce_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"
        hash1 = hash_password(password1)
        hash2 = hash_password(password2)
        assert hash1 != hash2


class TestPasswordValidation:
    """Tests for password validation function."""
    
    def test_valid_password(self):
        """Test validation of a valid password."""
        password = "SecurePass123"
        is_valid, errors = validate_password(password)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_password_too_short(self):
        """Test validation of password that is too short."""
        password = "Short1"
        is_valid, errors = validate_password(password)
        assert is_valid is False
        assert any("at least 8 characters" in error for error in errors)
    
    def test_password_no_uppercase(self):
        """Test validation of password without uppercase."""
        password = "password123"
        is_valid, errors = validate_password(password)
        assert is_valid is False
        assert any("uppercase" in error.lower() for error in errors)
    
    def test_password_no_lowercase(self):
        """Test validation of password without lowercase."""
        password = "PASSWORD123"
        is_valid, errors = validate_password(password)
        assert is_valid is False
        assert any("lowercase" in error.lower() for error in errors)
    
    def test_password_no_digit(self):
        """Test validation of password without digit."""
        password = "PasswordABC"
        is_valid, errors = validate_password(password)
        assert is_valid is False
        assert any("digit" in error.lower() for error in errors)


class TestJWTTokens:
    """Tests for JWT token functions."""
    
    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string."""
        data = {"sub": "user123"}
        token = create_access_token(data)
        assert isinstance(token, str)
    
    def test_decode_access_token_valid(self):
        """Test decoding a valid access token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
    
    def test_decode_access_token_with_custom_expiry(self):
        """Test decoding token with custom expiry."""
        data = {"sub": "user123"}
        token = create_access_token(data, expires_delta=timedelta(hours=2))
        decoded = decode_access_token(token)
        assert decoded is not None
        assert "exp" in decoded
    
    def test_decode_access_token_invalid(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)
        assert decoded is None
