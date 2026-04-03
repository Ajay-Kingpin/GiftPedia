import pytest
from pydantic import ValidationError
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from backend.app.main import RecommendationRequest, UserProfile, Product

class TestRecommendationRequest:
    def test_valid_request_creation(self):
        """Test creating a valid recommendation request"""
        request = RecommendationRequest(
            user_input="I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000",
            session_id="test-session-123",
            user_id="user-456"
        )
        
        assert request.user_input == "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
        assert request.session_id == "test-session-123"
        assert request.user_id == "user-456"

    def test_minimal_request_creation(self):
        """Test creating a request with only required fields"""
        request = RecommendationRequest(
            user_input="I need a gift for my brother"
        )
        
        assert request.user_input == "I need a gift for my brother"
        assert request.session_id is None
        assert request.user_id is None

    def test_empty_user_input_raises_validation_error(self):
        """Test that empty user_input raises validation error"""
        with pytest.raises(ValidationError):
            RecommendationRequest(user_input="")

    def test_none_user_input_raises_validation_error(self):
        """Test that None user_input raises validation error"""
        with pytest.raises(ValidationError):
            RecommendationRequest(user_input=None)

class TestUserProfile:
    def test_valid_profile_creation(self):
        """Test creating a valid user profile"""
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar", "audio"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
        )
        
        assert profile.recipient_age == 28
        assert profile.recipient_gender == "male"
        assert profile.interests == ["music", "guitar", "audio"]
        assert profile.relationship == "family"
        assert profile.occasion == "birthday"
        assert profile.budget_inr == 2000
        assert profile.constraints == []

    def test_profile_with_optional_null_fields(self):
        """Test profile with optional null fields"""
        profile = UserProfile(
            recipient_age=None,
            recipient_gender="unknown",
            interests=["reading"],
            relationship="friend",
            occasion="just_because",
            budget_inr=None,
            constraints=["vegan"]
        )
        
        assert profile.recipient_age is None
        assert profile.recipient_gender == "unknown"
        assert profile.budget_inr is None

    def test_invalid_gender_raises_validation_error(self):
        """Test that invalid gender raises validation error"""
        with pytest.raises(ValidationError):
            UserProfile(
                recipient_age=28,
                recipient_gender="invalid_gender",
                interests=["music"],
                relationship="family",
                occasion="birthday",
                budget_inr=2000,
                constraints=[]
            )

    def test_invalid_relationship_raises_validation_error(self):
        """Test that invalid relationship raises validation error"""
        with pytest.raises(ValidationError):
            UserProfile(
                recipient_age=28,
                recipient_gender="male",
                interests=["music"],
                relationship="invalid_relationship",
                occasion="birthday",
                budget_inr=2000,
                constraints=[]
            )

    def test_invalid_occasion_raises_validation_error(self):
        """Test that invalid occasion raises validation error"""
        with pytest.raises(ValidationError):
            UserProfile(
                recipient_age=28,
                recipient_gender="male",
                interests=["music"],
                relationship="family",
                occasion="invalid_occasion",
                budget_inr=2000,
                constraints=[]
            )

    def test_interests_must_be_list(self):
        """Test that interests must be a list"""
        with pytest.raises(ValidationError):
            UserProfile(
                recipient_age=28,
                recipient_gender="male",
                interests="music",  # Should be list, not string
                relationship="family",
                occasion="birthday",
                budget_inr=2000,
                constraints=[]
            )

    def test_constraints_must_be_list(self):
        """Test that constraints must be a list"""
        with pytest.raises(ValidationError):
            UserProfile(
                recipient_age=28,
                recipient_gender="male",
                interests=["music"],
                relationship="family",
                occasion="birthday",
                budget_inr=2000,
                constraints="vegan"  # Should be list, not string
            )

class TestProduct:
    def test_valid_product_creation(self):
        """Test creating a valid product"""
        product = Product(
            product_id="amz_B08N5WRWSN",
            name="Fender Custom Guitar Strap",
            category="Music & Instruments",
            subcategory="Guitar Straps",
            price_inr=1899.0,
            brand="Fender",
            image_url="https://example.com/image.jpg",
            affiliate_link="https://amazon.in/dp/B08N5WRWSN",
            confidence_score=5,
            explanation="Perfect for musicians who want comfort and style"
        )
        
        assert product.product_id == "amz_B08N5WRWSN"
        assert product.name == "Fender Custom Guitar Strap"
        assert product.category == "Music & Instruments"
        assert product.subcategory == "Guitar Straps"
        assert product.price_inr == 1899.0
        assert product.brand == "Fender"
        assert product.image_url == "https://example.com/image.jpg"
        assert product.affiliate_link == "https://amazon.in/dp/B08N5WRWSN"
        assert product.confidence_score == 5
        assert product.explanation == "Perfect for musicians who want comfort and style"

    def test_minimal_product_creation(self):
        """Test creating a product with only required fields"""
        product = Product(
            product_id="prod_123",
            name="Test Product",
            category="Test Category",
            subcategory="Test Subcategory",
            price_inr=999.0,
            image_url="https://example.com/test.jpg",
            affiliate_link="https://example.com/test-link"
        )
        
        assert product.product_id == "prod_123"
        assert product.brand is None
        assert product.confidence_score is None
        assert product.explanation is None

    def test_invalid_confidence_score_raises_validation_error(self):
        """Test that invalid confidence score raises validation error"""
        with pytest.raises(ValidationError):
            Product(
                product_id="prod_123",
                name="Test Product",
                category="Test Category",
                subcategory="Test Subcategory",
                price_inr=999.0,
                image_url="https://example.com/test.jpg",
                affiliate_link="https://example.com/test-link",
                confidence_score=10  # Should be 1-5
            )

    def test_negative_price_raises_validation_error(self):
        """Test that negative price raises validation error"""
        with pytest.raises(ValidationError):
            Product(
                product_id="prod_123",
                name="Test Product",
                category="Test Category",
                subcategory="Test Subcategory",
                price_inr=-100.0,  # Should be positive
                image_url="https://example.com/test.jpg",
                affiliate_link="https://example.com/test-link"
            )

class TestDataValidation:
    def test_email_format_in_user_input(self):
        """Test that email-like inputs are handled properly"""
        request = RecommendationRequest(
            user_input="I need a gift for my brother john.doe@example.com who loves music"
        )
        assert "john.doe@example.com" in request.user_input

    def test_special_characters_in_interests(self):
        """Test that special characters in interests are handled"""
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="female",
            interests=["cooking", "baking", "DIY crafts"],
            relationship="friend",
            occasion="birthday",
            budget_inr=1500,
            constraints=[]
        )
        assert "DIY crafts" in profile.interests

    def test_unicode_characters_in_product_name(self):
        """Test that unicode characters in product names are handled"""
        product = Product(
            product_id="prod_123",
            name="Café Espresso Machine - ₹2000",
            category="Kitchen Appliances",
            subcategory="Coffee Makers",
            price_inr=2000.0,
            image_url="https://example.com/cafe.jpg",
            affiliate_link="https://example.com/cafe-link"
        )
        assert "Café" in product.name
        assert "₹" in product.name

if __name__ == "__main__":
    pytest.main([__file__])
