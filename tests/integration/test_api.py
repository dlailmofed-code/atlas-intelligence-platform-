"""
Integration tests for API endpoints.
"""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "health" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data


class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123",
                "full_name": "New User",
                "company": "Test Company",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email."""
        # First registration
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "SecurePass123",
                "full_name": "First User",
            },
        )
        
        # Second registration with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "AnotherPass123",
                "full_name": "Second User",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_invalid_password(self, client):
        """Test registration with invalid password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user@example.com",
                "password": "weak",  # Too short
                "full_name": "Test User",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_success(self, client):
        """Test successful login."""
        # Register first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "SecurePass123",
                "full_name": "Login User",
            },
        )
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "SecurePass123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        # Register first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@example.com",
                "password": "SecurePass123",
                "full_name": "Test User",
            },
        )
        
        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "WrongPassword123",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "SomePassword123",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_logout(self, client):
        """Test logout endpoint."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == status.HTTP_200_OK


class TestOpportunitiesEndpoints:
    """Tests for opportunities endpoints."""
    
    def test_list_opportunities(self, client):
        """Test listing opportunities."""
        response = client.get("/api/v1/opportunities/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "has_next" in data
    
    def test_list_opportunities_with_pagination(self, client):
        """Test listing opportunities with pagination."""
        response = client.get("/api/v1/opportunities/?page=1&page_size=10")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10


class TestIntelligenceEndpoints:
    """Tests for intelligence endpoints."""
    
    def test_list_signals(self, client):
        """Test listing signals."""
        response = client.get("/api/v1/intelligence/signals/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_indicators(self, client):
        """Test getting intelligence indicators."""
        response = client.get("/api/v1/intelligence/indicators")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "opportunity_score" in data
        assert "demand_index" in data
        assert "generated_at" in data
