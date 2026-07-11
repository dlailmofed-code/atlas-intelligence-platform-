"""
ATLAS Platform - Authentication Unit Tests
"""


from backend.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    validate_password,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing functionality."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        hashed = hash_password(password)

        assert verify_password("WrongPassword", hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "Password1!"
        password2 = "Password2!"

        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        assert hash1 != hash2


class TestPasswordValidation:
    """Test password validation functionality."""

    def test_valid_password(self):
        """Test validation of a valid password."""
        password = "TestPassword123!"
        is_valid, errors = validate_password(password)

        assert is_valid is True
        assert len(errors) == 0

    def test_password_too_short(self):
        """Test validation of a password that is too short."""
        password = "Short1!"
        is_valid, errors = validate_password(password)

        assert is_valid is False
        assert len(errors) > 0

    def test_password_no_uppercase(self):
        """Test validation of a password without uppercase."""
        password = "password123"
        is_valid, _errors = validate_password(password)

        # Should fail due to missing uppercase
        assert is_valid is False

    def test_password_no_lowercase(self):
        """Test validation of a password without lowercase."""
        password = "PASSWORD123"
        is_valid, _errors = validate_password(password)

        # Should fail due to missing lowercase
        assert is_valid is False

    def test_password_no_digit(self):
        """Test validation of a password without digit."""
        password = "PasswordNoDigits"
        is_valid, _errors = validate_password(password)

        # Should fail due to missing digit
        assert is_valid is False


class TestJWTTokens:
    """Test JWT token functionality."""

    def test_create_access_token(self):
        """Test creating an access token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """Test decoding an access token."""
        data = {"sub": "user123", "email": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)

        assert decoded is None

    def test_access_token_contains_expiration(self):
        """Test that access token contains expiration."""
        data = {"sub": "user123"}
        token = create_access_token(data)
        decoded = decode_access_token(token)

        assert "exp" in decoded
        assert "iat" in decoded

    def test_create_refresh_token(self):
        """Test creating a refresh token."""
        data = {"sub": "user123"}
        token = create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_refresh_token(self):
        """Test decoding a refresh token."""
        data = {"sub": "user123"}
        token = create_refresh_token(data)
        decoded = decode_refresh_token(token)

        assert decoded is not None
        assert decoded["sub"] == "user123"
        assert decoded["type"] == "refresh"

    def test_access_token_not_recognized_as_refresh(self):
        """Test that access token is not recognized as refresh token."""
        data = {"sub": "user123"}
        token = create_access_token(data)
        decoded = decode_refresh_token(token)

        assert decoded is None
