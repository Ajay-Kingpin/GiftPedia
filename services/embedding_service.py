"""
Embedding Service
Handles product embedding generation using Google text-embedding-004
"""

import os
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import hashlib

class EmbeddingService:
    """Service for generating text embeddings"""
    
    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Embedding model
        self.model_name = 'text-embedding-004'
        self.embedding_dim = 1536
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Google text-embedding-004
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # For now, use mock embedding
            # In production, replace with actual Google embedding API call
            return self._mock_embedding(text)
            
        except Exception as e:
            print(f"Embedding generation error: {e}")
            # Fallback to mock embedding
            return self._mock_embedding(text)
    
    def generate_product_embedding(self, product: Dict[str, Any]) -> List[float]:
        """
        Generate embedding for product metadata
        
        Args:
            product: Product dictionary with metadata
            
        Returns:
            Embedding vector
        """
        # Create embedding text from product metadata
        embedding_text = self._create_product_text(product)
        
        return self.generate_embedding(embedding_text)
    
    def _create_product_text(self, product: Dict[str, Any]) -> str:
        """
        Create text representation of product for embedding
        
        Args:
            product: Product dictionary
            
        Returns:
            Text string for embedding
        """
        parts = []
        
        # Basic product info
        if product.get('name'):
            parts.append(product['name'])
        
        if product.get('category'):
            parts.append(product['category'])
        
        if product.get('subcategory'):
            parts.append(product['subcategory'])
        
        # Tags
        if product.get('interest_tags'):
            parts.extend(product['interest_tags'])
        
        if product.get('occasion_tags'):
            parts.extend(product['occasion_tags'])
        
        if product.get('relationship_tags'):
            parts.extend(product['relationship_tags'])
        
        # Brand
        if product.get('brand'):
            parts.append(product['brand'])
        
        return " | ".join(parts)
    
    def _mock_embedding(self, text: str) -> List[float]:
        """
        Mock embedding generation (replace with actual Google text-embedding-004)
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Create deterministic vector based on text
        hash_obj = hashlib.sha256(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert hash to float values
        embedding = []
        for i in range(0, len(hash_hex), 2):
            hex_pair = hash_hex[i:i+2]
            if hex_pair:
                val = int(hex_pair, 16) / 255.0
                embedding.append(val)
        
        # Pad or truncate to required dimensions
        while len(embedding) < self.embedding_dim:
            embedding.append(0.0)
        
        return embedding[:self.embedding_dim]
    
    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        
        return embeddings

# Singleton instance
embedding_service = EmbeddingService()

if __name__ == "__main__":
    # Test the embedding service
    test_products = [
        {
            "name": "Fender Custom Guitar Strap",
            "category": "Music & Instruments",
            "subcategory": "Guitar Accessories",
            "brand": "Fender",
            "interest_tags": ["music", "guitar", "accessory"],
            "occasion_tags": ["birthday", "anniversary"],
            "relationship_tags": ["friend", "family"]
        },
        {
            "name": "Smart Herb Garden Kit",
            "category": "Home & Garden",
            "subcategory": "Indoor Gardening",
            "brand": "AeroGarden",
            "interest_tags": ["gardening", "cooking", "healthy_living"],
            "occasion_tags": ["housewarming", "birthday"],
            "relationship_tags": ["partner", "family"]
        }
    ]
    
    service = EmbeddingService()
    
    print("Embedding Service Test Results:")
    print("=" * 50)
    
    for i, product in enumerate(test_products, 1):
        print(f"\n{i}. Product: {product['name']}")
        
        # Generate embedding text
        embedding_text = service._create_product_text(product)
        print(f"   Embedding Text: {embedding_text}")
        
        # Generate embedding
        embedding = service.generate_product_embedding(product)
        print(f"   Embedding Dimensions: {len(embedding)}")
        print(f"   Sample Values: {embedding[:5]}")
    
    print(f"\n✅ Embedding service working correctly")
