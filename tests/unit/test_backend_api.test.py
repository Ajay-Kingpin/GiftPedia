import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from backend.app.main import app, RecommendationRequest, UserProfile, Product

client = TestClient(app)

class TestHealthEndpoint:
    def test_health_check_returns_healthy_status(self):
        """Test that health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

class TestRecommendationsEndpoint:
    def test_missing_api_key_returns_401(self):
        """Test that requests without API key are rejected"""
        request_data = {
            "user_input": "I need a gift for my brother"
        }
        response = client.post("/api/recommendations", json=request_data)
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]

    def test_invalid_api_key_returns_401(self):
        """Test that requests with invalid API key are rejected"""
        headers = {"Authorization": "Bearer invalid-key"}
        request_data = {
            "user_input": "I need a gift for my brother"
        }
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        assert response.status_code == 401

    def test_valid_api_key_accepts_request(self):
        """Test that valid API key accepts requests"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
        }
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        assert response.status_code == 200

    def test_request_validation_requires_user_input(self):
        """Test that user_input is required"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {}  # Missing user_input
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        assert response.status_code == 422  # Validation error

    def test_request_validation_user_input_min_length(self):
        """Test that user_input meets minimum length requirement"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "short"  # Too short
        }
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        assert response.status_code == 422

    def test_optional_fields_are_not_required(self):
        """Test that session_id and user_id are optional"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "I need a gift for my brother who loves music and has a budget of ₹2000"
        }
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        assert response.status_code == 200

    def test_response_structure_is_correct(self):
        """Test that response has correct structure"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000",
            "session_id": "test-session-123"
        }
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendations" in data
        assert "profile" in data
        assert "processing_time" in data
        assert "session_id" in data

    def test_profile_structure_is_correct(self):
        """Test that profile data has correct structure"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
        }
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        profile = data["profile"]
        
        # Check all required fields exist
        assert "recipient_age" in profile
        assert "recipient_gender" in profile
        assert "interests" in profile
        assert "relationship" in profile
        assert "occasion" in profile
        assert "budget_inr" in profile
        assert "constraints" in profile
        
        # Check data types
        assert isinstance(profile["interests"], list)
        assert isinstance(profile["constraints"], list)
        assert profile["recipient_age"] is None or isinstance(profile["recipient_age"], int)

    def test_recommendations_structure_is_correct(self):
        """Test that recommendations have correct structure"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "I need a birthday gift for my brother"
        }
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data["recommendations"]
        
        assert isinstance(recommendations, list)
        if recommendations:  # If there are recommendations
            product = recommendations[0]
            required_fields = [
                "product_id", "name", "category", "subcategory", 
                "price_inr", "image_url", "affiliate_link"
            ]
            for field in required_fields:
                assert field in product

    def test_processing_time_is_returned(self):
        """Test that processing time is calculated and returned"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "I need a gift for my brother"
        }
        
        start_time = time.time()
        response = client.post("/api/recommendations", json=request_data, headers=headers)
        end_time = time.time()
        
        assert response.status_code == 200
        data = response.json()
        
        # Processing time should be reasonable (between start and end time)
        processing_time = data["processing_time"]
        assert 0 <= processing_time <= (end_time - start_time + 0.1)  # Add small buffer

    def test_session_id_is_preserved_or_generated(self):
        """Test that session_id is preserved or generated"""
        headers = {"Authorization": "Bearer dev-api-key"}
        
        # Test with provided session_id
        request_data_with_session = {
            "user_input": "I need a gift for my brother",
            "session_id": "custom-session-123"
        }
        response = client.post("/api/recommendations", json=request_data_with_session, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "custom-session-123"
        
        # Test without session_id (should generate one)
        request_data_without_session = {
            "user_input": "I need a gift for my sister"
        }
        response = client.post("/api/recommendations", json=request_data_without_session, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"].startswith("session_")

class TestRateLimiting:
    def test_rate_limiting_is_enforced(self):
        """Test that rate limiting prevents excessive requests"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "I need a gift for my brother"
        }
        
        # Make many requests to test rate limiting
        responses = []
        for i in range(510):  # Exceed the 500 limit
            response = client.post("/api/recommendations", json=request_data, headers=headers)
            responses.append(response.status_code)
            if response.status_code == 429:
                break
        
        # Should eventually hit rate limit
        assert 429 in responses
        assert "Rate limit exceeded" in responses[-1] if responses[-1] == 429 else True

class TestErrorHandling:
    def test_internal_server_error_handling(self):
        """Test that internal errors are handled gracefully"""
        headers = {"Authorization": "Bearer dev-api-key"}
        request_data = {
            "user_input": "I need a gift for my brother"
        }
        
        # Mock an internal error
        with patch('backend.app.main.time.time', side_effect=Exception("Internal error")):
            response = client.post("/api/recommendations", json=request_data, headers=headers)
            assert response.status_code == 500
            assert "Internal server error" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main([__file__])
