import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'agents', 'filter_rank'))

from agent import FilterRankAgent, Product

class TestFilterRankAgent:
    """Test cases for Agent 3: Filter & Rank"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        os.environ['PINECONE_API_KEY'] = 'test-pinecone-key'
        os.environ['PINECONE_ENVIRONMENT'] = 'us-west1-gcp'
        os.environ['PINECONE_INDEX_NAME'] = 'giftpedia_products_v1'
        
        # Create agent instance with mocked Pinecone
        with patch('agent.pinecone') as mock_pinecone:
            mock_pinecone.list_indexes.return_value = ['giftpedia_products_v1']
            mock_index = Mock()
            mock_pinecone.Index.return_value = mock_index
            
            self.agent = FilterRankAgent()
            self.mock_index = mock_index

    def test_product_model_creation(self):
        """Test Product model creation with valid data"""
        product = Product(
            product_id="prod_001",
            name="Fender Guitar Strap",
            category="Music & Instruments",
            subcategory="Guitar Accessories",
            price_inr=1899.0,
            brand="Fender",
            occasion_tags=["birthday"],
            relationship_tags=["friend"],
            interest_tags=["music", "guitar"],
            image_url="https://example.com/image.jpg",
            affiliate_link="https://example.com/affiliate",
            is_active=True
        )
        
        assert product.product_id == "prod_001"
        assert product.name == "Fender Guitar Strap"
        assert product.price_inr == 1899.0
        assert "music" in product.interest_tags

    def test_generate_search_query(self):
        """Test search query generation"""
        # Mock profile and concepts
        from agents.profile_analyzer import UserProfile
        from agents.creative_idea import GiftConcept
        
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
        )
        
        concepts = [
            GiftConcept(
                concept="Custom guitar accessories",
                category="Music",
                reasoning="Perfect for music enthusiast"
            )
        ]
        
        # Generate query
        query = self.agent.generate_search_query(profile, concepts)
        
        # Assertions
        assert "music" in query
        assert "guitar" in query
        assert "male" in query

    def test_search_similar_products(self):
        """Test product search functionality"""
        # Mock Pinecone response
        mock_response = {
            'matches': [
                {
                    'id': 'prod_001',
                    'score': 0.95,
                    'values': [0.1, 0.2, 0.3],
                    'metadata': {
                        'name': 'Fender Guitar Strap',
                        'category': 'Music & Instruments',
                        'price_inr': 1899.0,
                        'brand': 'Fender',
                        'interest_tags': ['music', 'guitar'],
                        'occasion_tags': ['birthday'],
                        'relationship_tags': ['friend'],
                        'is_active': True
                    }
                }
            ]
        }
        
        self.mock_index.query.return_value = mock_response
        
        # Search
        results = self.agent.search_similar_products("music guitar accessories")
        
        # Assertions
        assert len(results) == 1
        assert results[0]['product'].name == "Fender Guitar Strap"
        assert results[0]['similarity_score'] == 0.95

    def test_filter_by_budget(self):
        """Test budget filtering"""
        products = [
            {
                'product': Product(
                    product_id="prod_001",
                    name="Budget Guitar",
                    price_inr=1500.0
                ),
                'similarity_score': 0.9
            },
            {
                'product': Product(
                    product_id="prod_002",
                    name="Expensive Guitar",
                    price_inr=5000.0
                ),
                'similarity_score': 0.8
            }
        ]
        
        # Filter by budget
        filtered = self.agent.filter_by_budget(products, 2000)
        
        # Assertions
        assert len(filtered) == 1
        assert filtered[0]['product'].name == "Budget Guitar"

    def test_filter_by_constraints(self):
        """Test constraint filtering"""
        products = [
            {
                'product': Product(
                    product_id="prod_001",
                    name="Eco-friendly Gift",
                    price_inr=1000.0
                ),
                'similarity_score': 0.9
            },
            {
                'product': Product(
                    product_id="prod_002",
                    name="Plastic Toy",
                    price_inr=500.0
                ),
                'similarity_score': 0.8
            }
        ]
        
        # Filter by constraints
        filtered = self.agent.filter_by_constraints(products, ["no plastic"])
        
        # Assertions
        assert len(filtered) == 1
        assert filtered[0]['product'].name == "Eco-friendly Gift"

    def test_rank_products(self):
        """Test product ranking"""
        from agents.profile_analyzer import UserProfile
        
        products = [
            {
                'product': Product(
                    product_id="prod_001",
                    name="Perfect Match",
                    price_inr=1500.0,
                    interest_tags=["music", "guitar"],
                    occasion_tags=["birthday"],
                    relationship_tags=["family"]
                ),
                'similarity_score': 0.8
            },
            {
                'product': Product(
                    product_id="prod_002",
                    name="Poor Match",
                    price_inr=3000.0,
                    interest_tags=["cooking"],
                    occasion_tags=["anniversary"],
                    relationship_tags=["colleague"]
                ),
                'similarity_score': 0.6
            }
        ]
        
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
        )
        
        # Rank products
        ranked = self.agent.rank_products(products, profile)
        
        # Assertions
        assert len(ranked) == 2
        assert ranked[0]['product'].name == "Perfect Match"
        assert ranked[0]['final_score'] > ranked[1]['final_score']

    def test_filter_and_rank_integration(self):
        """Test complete filter and rank workflow"""
        # Mock Pinecone response
        mock_response = {
            'matches': [
                {
                    'id': 'prod_001',
                    'score': 0.95,
                    'values': [0.1, 0.2, 0.3],
                    'metadata': {
                        'name': 'Fender Guitar Strap',
                        'category': 'Music & Instruments',
                        'price_inr': 1899.0,
                        'brand': 'Fender',
                        'interest_tags': ['music', 'guitar'],
                        'occasion_tags': ['birthday'],
                        'relationship_tags': ['family'],
                        'is_active': True
                    }
                },
                {
                    'id': 'prod_002',
                    'score': 0.85,
                    'values': [0.2, 0.3, 0.4],
                    'metadata': {
                        'name': 'Plastic Guitar Pick',
                        'category': 'Music & Instruments',
                        'price_inr': 100.0,
                        'brand': 'Generic',
                        'interest_tags': ['music'],
                        'occasion_tags': ['birthday'],
                        'relationship_tags': ['friend'],
                        'is_active': True
                    }
                }
            ]
        }
        
        self.mock_index.query.return_value = mock_response
        
        # Mock profile and concepts
        from agents.profile_analyzer import UserProfile
        from agents.creative_idea import GiftConcept
        
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=["no plastic"]
        )
        
        concepts = [
            GiftConcept(
                concept="Custom guitar accessories",
                category="Music",
                reasoning="Perfect for music enthusiast"
            )
        ]
        
        # Run filter and rank
        results = self.agent.filter_and_rank(profile, concepts)
        
        # Assertions
        assert len(results) == 1  # Only non-plastic product should remain
        assert results[0]['product'].name == "Fender Guitar Strap"
        assert 'final_score' in results[0]

    def test_mock_embedding_generation(self):
        """Test mock embedding generation"""
        text = "music guitar accessories"
        embedding = self.agent._mock_embedding(text)
        
        # Assertions
        assert len(embedding) == 1536  # Correct dimensions
        assert all(isinstance(x, float) for x in embedding)

    def test_missing_pinecone_api_key(self):
        """Test initialization without Pinecone API key"""
        # Remove API key from environment
        if 'PINECONE_API_KEY' in os.environ:
            del os.environ['PINECONE_API_KEY']
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="PINECONE_API_KEY environment variable not set"):
            FilterRankAgent()

    def test_search_error_handling(self):
        """Test search error handling"""
        # Mock Pinecone error
        self.mock_index.query.side_effect = Exception("Pinecone error")
        
        # Search should return empty list
        results = self.agent.search_similar_products("test query")
        assert results == []

    def test_empty_product_list_filtering(self):
        """Test filtering with empty product list"""
        # Test budget filtering
        filtered = self.agent.filter_by_budget([], 1000)
        assert filtered == []
        
        # Test constraint filtering
        filtered = self.agent.filter_by_constraints([], ["no plastic"])
        assert filtered == []

    def test_ranking_with_no_profile(self):
        """Test ranking with minimal profile data"""
        from agents.profile_analyzer import UserProfile
        
        products = [
            {
                'product': Product(
                    product_id="prod_001",
                    name="Test Product",
                    price_inr=1000.0
                ),
                'similarity_score': 0.8
            }
        ]
        
        profile = UserProfile()  # Default empty profile
        
        # Should not raise error
        ranked = self.agent.rank_products(products, profile)
        assert len(ranked) == 1

if __name__ == "__main__":
    pytest.main([__file__])
