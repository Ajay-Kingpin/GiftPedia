import pytest
import os
from unittest.mock import Mock, patch, MagicMock
import sys

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'services'))

from pinecone_service import PineconeService

class TestPineconeService:
    """Test cases for Pinecone Service"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        os.environ['PINECONE_API_KEY'] = 'test-pinecone-key'
        os.environ['PINECONE_ENVIRONMENT'] = 'us-west1-gcp'
        os.environ['PINECONE_INDEX_NAME'] = 'giftpedia_products_v1'
        
        # Create service instance with mocked Pinecone
        with patch('pinecone_service.pinecone') as mock_pinecone:
            mock_pinecone.list_indexes.return_value = ['giftpedia_products_v1']
            mock_index = Mock()
            mock_pinecone.Index.return_value = mock_index
            
            self.service = PineconeService()
            self.mock_pinecone = mock_pinecone
            self.mock_index = mock_index

    def test_pinecone_service_initialization(self):
        """Test Pinecone service initialization"""
        assert self.service.index_name == 'giftpedia_products_v1'
        assert self.service.embedding_dim == 1536
        assert self.service.index == self.mock_index

    def test_create_index(self):
        """Test index creation"""
        # Mock index doesn't exist
        self.mock_pinecone.list_indexes.return_value = []
        
        # Create service
        with patch('pinecone_service.pinecone') as mock_pinecone:
            mock_pinecone.list_indexes.return_value = []
            mock_index = Mock()
            mock_pinecone.Index.return_value = mock_index
            
            service = PineconeService()
            
            # Should create index
            mock_pinecone.create_index.assert_called_once_with(
                name='giftpedia_products_v1',
                dimension=1536,
                metric='cosine',
                pod_type='s1'
            )

    def test_upsert_product(self):
        """Test product upsert"""
        product = {
            "product_id": "prod_001",
            "name": "Fender Guitar Strap",
            "category": "Music & Instruments",
            "subcategory": "Guitar Accessories",
            "price_inr": 1899.0,
            "brand": "Fender",
            "interest_tags": ["music", "guitar"],
            "occasion_tags": ["birthday"],
            "relationship_tags": ["friend"],
            "image_url": "https://example.com/image.jpg",
            "affiliate_link": "https://example.com/affiliate",
            "is_active": True
        }
        
        # Mock embedding service
        with patch('pinecone_service.embedding_service') as mock_embedding:
            mock_embedding.generate_product_embedding.return_value = [0.1, 0.2, 0.3]
            
            product_id = self.service.upsert_product(product)
            
            # Assertions
            assert product_id == "prod_001"
            self.mock_index.upsert.assert_called_once()
            
            # Check upsert call arguments
            call_args = self.mock_index.upsert.call_args[1]
            vectors = call_args['vectors']
            assert len(vectors) == 1
            assert vectors[0]['id'] == "prod_001"
            assert vectors[0]['values'] == [0.1, 0.2, 0.3]
            assert vectors[0]['metadata']['name'] == "Fender Guitar Strap"

    def test_upsert_product_without_id(self):
        """Test product upsert without product ID"""
        product = {
            "name": "Test Product",
            "category": "Test Category",
            "price_inr": 1000.0
        }
        
        # Mock embedding service
        with patch('pinecone_service.embedding_service') as mock_embedding:
            mock_embedding.generate_product_embedding.return_value = [0.1, 0.2, 0.3]
            
            product_id = self.service.upsert_product(product)
            
            # Should generate UUID
            assert product_id is not None
            assert len(product_id) > 0

    def test_batch_upsert_products(self):
        """Test batch product upsert"""
        products = [
            {
                "product_id": "prod_001",
                "name": "Product 1",
                "category": "Category 1",
                "price_inr": 1000.0
            },
            {
                "product_id": "prod_002",
                "name": "Product 2",
                "category": "Category 2",
                "price_inr": 2000.0
            }
        ]
        
        # Mock embedding service
        with patch('pinecone_service.embedding_service') as mock_embedding:
            mock_embedding.batch_generate_embeddings.return_value = [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6]
            ]
            
            product_ids = self.service.batch_upsert_products(products)
            
            # Assertions
            assert len(product_ids) == 2
            assert product_ids[0] == "prod_001"
            assert product_ids[1] == "prod_002"
            self.mock_index.upsert.assert_called_once()

    def test_search_products(self):
        """Test product search"""
        # Mock search response
        mock_response = {
            'matches': [
                {
                    'id': 'prod_001',
                    'score': 0.95,
                    'values': [0.1, 0.2, 0.3],
                    'metadata': {
                        'name': 'Fender Guitar Strap',
                        'category': 'Music & Instruments',
                        'price_inr': 1899.0
                    }
                }
            ]
        }
        
        self.mock_index.query.return_value = mock_response
        
        # Search
        results = self.service.search_products([0.1, 0.2, 0.3])
        
        # Assertions
        assert len(results) == 1
        assert results[0]['id'] == 'prod_001'
        assert results[0]['score'] == 0.95
        assert results[0]['metadata']['name'] == 'Fender Guitar Strap'

    def test_search_products_with_filters(self):
        """Test product search with filters"""
        # Mock search response
        mock_response = {'matches': []}
        self.mock_index.query.return_value = mock_response
        
        # Search with filters
        filters = {'category': 'Music & Instruments'}
        results = self.service.search_products([0.1, 0.2, 0.3], filters=filters)
        
        # Should call query with filters
        self.mock_index.query.assert_called_once_with(
            vector=[0.1, 0.2, 0.3],
            top_k=20,
            include_metadata=True,
            filter=filters
        )

    def test_get_product_by_id(self):
        """Test getting product by ID"""
        # Mock fetch response
        mock_response = {
            'vectors': {
                'prod_001': {
                    'values': [0.1, 0.2, 0.3],
                    'metadata': {
                        'name': 'Fender Guitar Strap',
                        'category': 'Music & Instruments'
                    }
                }
            }
        }
        
        self.mock_index.fetch.return_value = mock_response
        
        # Get product
        product = self.service.get_product_by_id('prod_001')
        
        # Assertions
        assert product is not None
        assert product['id'] == 'prod_001'
        assert product['metadata']['name'] == 'Fender Guitar Strap'

    def test_get_product_by_id_not_found(self):
        """Test getting non-existent product"""
        # Mock empty response
        mock_response = {'vectors': {}}
        self.mock_index.fetch.return_value = mock_response
        
        # Get product
        product = self.service.get_product_by_id('nonexistent')
        
        # Should return None
        assert product is None

    def test_delete_product(self):
        """Test product deletion"""
        # Delete product
        success = self.service.delete_product('prod_001')
        
        # Assertions
        assert success is True
        self.mock_index.delete.assert_called_once_with(ids=['prod_001'])

    def test_delete_product_error(self):
        """Test product deletion error"""
        # Mock delete error
        self.mock_index.delete.side_effect = Exception("Delete error")
        
        # Delete product
        success = self.service.delete_product('prod_001')
        
        # Should return False
        assert success is False

    def test_get_index_stats(self):
        """Test getting index statistics"""
        # Mock stats response
        mock_stats = {
            'dimension': 1536,
            'indexFullness': 0.1,
            'namespaces': {},
            'totalVectorCount': 100
        }
        
        self.mock_index.describe_index_stats.return_value = mock_stats
        
        # Get stats
        stats = self.service.get_index_stats()
        
        # Assertions
        assert stats['dimension'] == 1536
        assert stats['totalVectorCount'] == 100

    def test_get_index_stats_error(self):
        """Test getting index statistics error"""
        # Mock stats error
        self.mock_index.describe_index_stats.side_effect = Exception("Stats error")
        
        # Get stats
        stats = self.service.get_index_stats()
        
        # Should return empty dict
        assert stats == {}

    def test_initialize_sample_data(self):
        """Test sample data initialization"""
        # Mock embedding service
        with patch('pinecone_service.embedding_service') as mock_embedding:
            mock_embedding.batch_generate_embeddings.return_value = [
                [0.1] * 1536,
                [0.2] * 1536,
                [0.3] * 1536,
                [0.4] * 1536,
                [0.5] * 1536
            ]
            
            # Initialize sample data
            product_ids = self.service.initialize_sample_data()
            
            # Assertions
            assert len(product_ids) == 5
            assert 'prod_001' in product_ids
            assert 'prod_005' in product_ids
            self.mock_index.upsert.assert_called_once()

    def test_missing_pinecone_api_key(self):
        """Test initialization without Pinecone API key"""
        # Remove API key from environment
        if 'PINECONE_API_KEY' in os.environ:
            del os.environ['PINECONE_API_KEY']
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="PINECONE_API_KEY environment variable not set"):
            PineconeService()

    def test_index_not_found(self):
        """Test initialization when index doesn't exist"""
        # Mock index doesn't exist and creation fails
        self.mock_pinecone.list_indexes.return_value = []
        self.mock_pinecone.create_index.side_effect = Exception("Create error")
        
        # Should still work (create_index is called in __init__)
        with patch('pinecone_service.pinecone') as mock_pinecone:
            mock_pinecone.list_indexes.return_value = []
            mock_pinecone.create_index.side_effect = Exception("Create error")
            mock_index = Mock()
            mock_pinecone.Index.return_value = mock_index
            
            # Should not raise error during creation
            service = PineconeService()

    def test_search_products_error(self):
        """Test search error handling"""
        # Mock search error
        self.mock_index.query.side_effect = Exception("Search error")
        
        # Search should handle error gracefully
        results = self.service.search_products([0.1, 0.2, 0.3])
        assert results == []

if __name__ == "__main__":
    pytest.main([__file__])
