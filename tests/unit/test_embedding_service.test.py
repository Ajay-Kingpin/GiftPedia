import pytest
import os
from unittest.mock import Mock, patch
import sys

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'services'))

from embedding_service import EmbeddingService

class TestEmbeddingService:
    """Test cases for Embedding Service"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        os.environ['GEMINI_API_KEY'] = 'test-gemini-key'
        
        # Create service instance
        self.service = EmbeddingService()

    def test_embedding_service_initialization(self):
        """Test embedding service initialization"""
        assert self.service.model_name == 'text-embedding-004'
        assert self.service.embedding_dim == 1536

    def test_generate_embedding(self):
        """Test embedding generation"""
        text = "Fender guitar strap for music lovers"
        embedding = self.service.generate_embedding(text)
        
        # Assertions
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)
        assert all(0.0 <= x <= 1.0 for x in embedding)

    def test_generate_product_embedding(self):
        """Test product embedding generation"""
        product = {
            "name": "Fender Guitar Strap",
            "category": "Music & Instruments",
            "subcategory": "Guitar Accessories",
            "brand": "Fender",
            "interest_tags": ["music", "guitar", "accessory"],
            "occasion_tags": ["birthday", "anniversary"],
            "relationship_tags": ["friend", "family"]
        }
        
        embedding = self.service.generate_product_embedding(product)
        
        # Assertions
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

    def test_create_product_text(self):
        """Test product text creation for embedding"""
        product = {
            "name": "Fender Guitar Strap",
            "category": "Music & Instruments",
            "subcategory": "Guitar Accessories",
            "brand": "Fender",
            "interest_tags": ["music", "guitar", "accessory"],
            "occasion_tags": ["birthday", "anniversary"],
            "relationship_tags": ["friend", "family"]
        }
        
        text = self.service._create_product_text(product)
        
        # Assertions
        assert "Fender Guitar Strap" in text
        assert "Music & Instruments" in text
        assert "Guitar Accessories" in text
        assert "Fender" in text
        assert "music" in text
        assert "guitar" in text
        assert "accessory" in text
        assert "birthday" in text
        assert "anniversary" in text
        assert "friend" in text
        assert "family" in text

    def test_create_product_text_minimal(self):
        """Test product text creation with minimal data"""
        product = {
            "name": "Simple Product"
        }
        
        text = self.service._create_product_text(product)
        
        # Assertions
        assert text == "Simple Product"

    def test_create_product_text_empty(self):
        """Test product text creation with empty product"""
        product = {}
        
        text = self.service._create_product_text(product)
        
        # Assertions
        assert text == ""

    def test_batch_generate_embeddings(self):
        """Test batch embedding generation"""
        texts = [
            "Fender guitar strap",
            "Smart herb garden kit",
            "Vinyl record collection"
        ]
        
        embeddings = self.service.batch_generate_embeddings(texts)
        
        # Assertions
        assert len(embeddings) == 3
        for embedding in embeddings:
            assert len(embedding) == 1536
            assert all(isinstance(x, float) for x in embedding)

    def test_mock_embedding_deterministic(self):
        """Test that mock embeddings are deterministic"""
        text = "test text"
        embedding1 = self.service._mock_embedding(text)
        embedding2 = self.service._mock_embedding(text)
        
        # Should be identical
        assert embedding1 == embedding2

    def test_mock_embedding_different_texts(self):
        """Test that different texts produce different embeddings"""
        text1 = "guitar music"
        text2 = "cooking gardening"
        
        embedding1 = self.service._mock_embedding(text1)
        embedding2 = self.service._mock_embedding(text2)
        
        # Should be different
        assert embedding1 != embedding2

    def test_missing_gemini_api_key(self):
        """Test initialization without Gemini API key"""
        # Remove API key from environment
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable not set"):
            EmbeddingService()

    def test_embedding_error_handling(self):
        """Test embedding generation error handling"""
        # This would test actual API errors, but since we're using mock embeddings,
        # this test ensures the fallback works
        text = "test text"
        embedding = self.service.generate_embedding(text)
        
        # Should still return embedding even if API fails
        assert len(embedding) == 1536

    def test_embedding_dimensions_consistency(self):
        """Test that all embeddings have consistent dimensions"""
        texts = [
            "Short text",
            "A much longer text with many more words to test dimension consistency",
            "Medium length text here"
        ]
        
        embeddings = self.service.batch_generate_embeddings(texts)
        
        # All should have same dimensions
        for embedding in embeddings:
            assert len(embedding) == 1536

    def test_embedding_value_ranges(self):
        """Test that embedding values are in expected range"""
        text = "test text for value range validation"
        embedding = self.service.generate_embedding(text)
        
        # Values should be between 0 and 1 (mock implementation)
        assert all(0.0 <= x <= 1.0 for x in embedding)

    def test_product_embedding_with_special_characters(self):
        """Test product embedding with special characters"""
        product = {
            "name": "Guitar™ Pro - Deluxe Edition",
            "category": "Music & Instruments",
            "subcategory": "Guitar Accessories",
            "brand": "Fender®",
            "interest_tags": ["music", "guitar", "pro"],
            "occasion_tags": ["birthday", "anniversary"],
            "relationship_tags": ["friend", "family"]
        }
        
        # Should not raise error
        embedding = self.service.generate_product_embedding(product)
        assert len(embedding) == 1536

    def test_empty_text_embedding(self):
        """Test embedding generation with empty text"""
        embedding = self.service.generate_embedding("")
        
        # Should still return valid embedding
        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

if __name__ == "__main__":
    pytest.main([__file__])
