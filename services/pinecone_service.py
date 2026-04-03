"""
Pinecone Service
Handles Pinecone vector database operations
"""

import os
import json
import pinecone
from typing import List, Dict, Any, Optional
import uuid

from services.embedding_service import embedding_service

class PineconeService:
    """Service for Pinecone vector database operations"""
    
    def __init__(self):
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        environment = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
        index_name = os.getenv("PINECONE_INDEX_NAME", "giftpedia_products_v1")
        
        # Initialize Pinecone client (older API)
        pinecone.init(api_key=api_key, environment=environment)
        
        self.index_name = index_name
        self.embedding_dim = 1536
        
        # Create index if it doesn't exist
        if index_name not in pinecone.list_indexes():
            self._create_index()
        
        # Connect to index
        self.index = pinecone.Index(index_name)
    
    def _create_index(self):
        """Create Pinecone index with proper configuration"""
        pinecone.create_index(
            name=self.index_name,
            dimension=self.embedding_dim,
            metric="cosine",
            pod_type="s1"  # Starter pod type (free tier compatible)
        )
        print(f"✅ Created Pinecone index: {self.index_name}")
    
    def upsert_product(self, product: Dict[str, Any]) -> str:
        """
        Upsert product to Pinecone
        
        Args:
            product: Product dictionary
            
        Returns:
            Product ID
        """
        # Generate product ID if not provided
        product_id = product.get('product_id') or str(uuid.uuid4())
        
        # Generate embedding
        embedding = embedding_service.generate_product_embedding(product)
        
        # Prepare metadata
        metadata = {
            'name': product.get('name', ''),
            'category': product.get('category', ''),
            'subcategory': product.get('subcategory', ''),
            'price_inr': product.get('price_inr', 0.0),
            'brand': product.get('brand', ''),
            'occasion_tags': product.get('occasion_tags', []),
            'relationship_tags': product.get('relationship_tags', []),
            'interest_tags': product.get('interest_tags', []),
            'image_url': product.get('image_url', ''),
            'affiliate_link': product.get('affiliate_link', ''),
            'is_active': product.get('is_active', True)
        }
        
        # Upsert to Pinecone
        self.index.upsert(
            vectors=[{
                'id': product_id,
                'values': embedding,
                'metadata': metadata
            }]
        )
        
        return product_id
    
    def batch_upsert_products(self, products: List[Dict[str, Any]]) -> List[str]:
        """
        Batch upsert products to Pinecone
        
        Args:
            products: List of product dictionaries
            
        Returns:
            List of product IDs
        """
        vectors = []
        product_ids = []
        
        for product in products:
            # Generate product ID if not provided
            product_id = product.get('product_id') or str(uuid.uuid4())
            product_ids.append(product_id)
            
            # Generate embedding
            embedding = embedding_service.generate_product_embedding(product)
            
            # Prepare metadata
            metadata = {
                'name': product.get('name', ''),
                'category': product.get('category', ''),
                'subcategory': product.get('subcategory', ''),
                'price_inr': product.get('price_inr', 0.0),
                'brand': product.get('brand', ''),
                'occasion_tags': product.get('occasion_tags', []),
                'relationship_tags': product.get('relationship_tags', []),
                'interest_tags': product.get('interest_tags', []),
                'image_url': product.get('image_url', ''),
                'affiliate_link': product.get('affiliate_link', ''),
                'is_active': product.get('is_active', True)
            }
            
            vectors.append({
                'id': product_id,
                'values': embedding,
                'metadata': metadata
            })
        
        # Batch upsert to Pinecone
        self.index.upsert(vectors=vectors)
        
        return product_ids
    
    def search_products(self, query_embedding: List[float], top_k: int = 20, 
                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search products using vector similarity
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of search results
        """
        search_args = {
            'vector': query_embedding,
            'top_k': top_k,
            'include_metadata': True
        }
        
        if filters:
            search_args['filter'] = filters
        
        results = self.index.query(**search_args)
        
        return results['matches']
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Get product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Product data or None
        """
        try:
            result = self.index.fetch(ids=[product_id])
            
            if result['vectors']:
                vector_data = result['vectors'][product_id]
                return {
                    'id': product_id,
                    'values': vector_data['values'],
                    'metadata': vector_data['metadata']
                }
            
            return None
            
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete product from Pinecone
        
        Args:
            product_id: Product ID
            
        Returns:
            Success status
        """
        try:
            self.index.delete(ids=[product_id])
            return True
        except Exception as e:
            print(f"Error deleting product {product_id}: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get Pinecone index statistics
        
        Returns:
            Index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}
    
    def initialize_sample_data(self) -> List[str]:
        """
        Initialize Pinecone with sample product data
        
        Returns:
            List of product IDs
        """
        sample_products = [
            {
                "product_id": "prod_001",
                "name": "Fender Custom Guitar Strap",
                "category": "Music & Instruments",
                "subcategory": "Guitar Accessories",
                "price_inr": 1899.0,
                "brand": "Fender",
                "interest_tags": ["music", "guitar", "accessory"],
                "occasion_tags": ["birthday", "anniversary"],
                "relationship_tags": ["friend", "family"],
                "image_url": "https://example.com/guitar-strap.jpg",
                "affiliate_link": "https://example.com/affiliate/guitar-strap",
                "is_active": True
            },
            {
                "product_id": "prod_002",
                "name": "Smart Herb Garden Kit",
                "category": "Home & Garden",
                "subcategory": "Indoor Gardening",
                "price_inr": 4999.0,
                "brand": "AeroGarden",
                "interest_tags": ["gardening", "cooking", "healthy_living"],
                "occasion_tags": ["housewarming", "birthday"],
                "relationship_tags": ["partner", "family"],
                "image_url": "https://example.com/herb-garden.jpg",
                "affiliate_link": "https://example.com/affiliate/herb-garden",
                "is_active": True
            },
            {
                "product_id": "prod_003",
                "name": "Vinyl Record Collection Starter Set",
                "category": "Music",
                "subcategory": "Vinyl Records",
                "price_inr": 2499.0,
                "brand": "Various",
                "interest_tags": ["music", "vinyl", "collecting"],
                "occasion_tags": ["birthday", "anniversary"],
                "relationship_tags": ["friend", "partner"],
                "image_url": "https://example.com/vinyl-set.jpg",
                "affiliate_link": "https://example.com/affiliate/vinyl-set",
                "is_active": True
            },
            {
                "product_id": "prod_004",
                "name": "Professional Yoga Mat",
                "category": "Fitness",
                "subcategory": "Yoga Equipment",
                "price_inr": 1299.0,
                "brand": "Manduka",
                "interest_tags": ["fitness", "yoga", "wellness"],
                "occasion_tags": ["birthday", "just_because"],
                "relationship_tags": ["friend", "colleague"],
                "image_url": "https://example.com/yoga-mat.jpg",
                "affiliate_link": "https://example.com/affiliate/yoga-mat",
                "is_active": True
            },
            {
                "product_id": "prod_005",
                "name": "Art Subscription Box",
                "category": "Art & Crafts",
                "subcategory": "Art Supplies",
                "price_inr": 1799.0,
                "brand": "ArtBox",
                "interest_tags": ["painting", "art", "creativity"],
                "occasion_tags": ["birthday", "anniversary"],
                "relationship_tags": ["friend", "family"],
                "image_url": "https://example.com/art-box.jpg",
                "affiliate_link": "https://example.com/affiliate/art-box",
                "is_active": True
            }
        ]
        
        # Batch upsert sample products
        product_ids = self.batch_upsert_products(sample_products)
        
        print(f"✅ Initialized Pinecone with {len(sample_products)} sample products")
        return product_ids

# Singleton instance
pinecone_service = PineconeService()

if __name__ == "__main__":
    # Test the Pinecone service
    print("🧪 Testing Pinecone Service...")
    
    try:
        service = PineconeService()
        
        # Initialize sample data
        product_ids = service.initialize_sample_data()
        
        # Get index stats
        stats = service.get_index_stats()
        print(f"Index Stats: {stats}")
        
        # Test search
        query_embedding = embedding_service.generate_embedding("music guitar accessories")
        results = service.search_products(query_embedding, top_k=3)
        
        print(f"\nSearch Results for 'music guitar accessories':")
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            print(f"{i}. {metadata['name']} - Score: {result['score']:.3f}")
        
        print("\n✅ Pinecone service working correctly")
        
    except Exception as e:
        print(f"❌ Pinecone service error: {e}")
        print("Note: This is expected if Pinecone credentials are not configured")
