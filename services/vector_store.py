"""
Vector Store Service using FAISS (Free, Local, No Login Required)
Alternative to Pinecone for vector similarity search
"""

import os
import json
import numpy as np
import pickle
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
import faiss

class ProductVector(BaseModel):
    """Product vector model for FAISS storage"""
    product_id: str
    name: str
    category: str
    subcategory: str
    price_inr: float
    brand: str
    occasion_tags: List[str] = []
    relationship_tags: List[str] = []
    interest_tags: List[str] = []
    image_url: Optional[str] = None
    affiliate_link: Optional[str] = None
    is_active: bool = True
    embedding: List[float]

class FAISSVectorStore:
    """FAISS-based vector store for product similarity search"""
    
    def __init__(self, index_file: str = "data/faiss_index.bin", 
                 metadata_file: str = "data/product_metadata.pkl"):
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.index = None
        self.metadata = []
        self.dimension = None
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(index_file), exist_ok=True)
        
        # Load existing index or create new one
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one"""
        try:
            if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
                print(f"Loading existing FAISS index from {self.index_file}")
                self.index = faiss.read_index(self.index_file)
                
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                if self.metadata:
                    self.dimension = len(self.metadata[0].embedding)
                    print(f"Loaded {len(self.metadata)} products with dimension {self.dimension}")
                else:
                    self.dimension = 1536  # Default for OpenAI embeddings
                    print("Empty metadata, using default dimension 1536")
            else:
                print("Creating new FAISS index")
                self.dimension = 1536  # Default for OpenAI embeddings
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = []
        except Exception as e:
            print(f"Error loading index: {e}")
            print("Creating new FAISS index")
            self.dimension = 1536
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
    
    def add_product(self, product: ProductVector):
        """Add a product to the vector store"""
        if self.index is None:
            self._load_or_create_index()
        
        # Convert embedding to numpy array
        embedding_array = np.array(product.embedding, dtype=np.float32).reshape(1, -1)
        
        # Add to FAISS index
        self.index.add(embedding_array)
        
        # Add to metadata
        self.metadata.append(product)
        
        print(f"Added product {product.product_id} to vector store")
    
    def add_products(self, products: List[ProductVector]):
        """Add multiple products to the vector store"""
        if self.index is None:
            self._load_or_create_index()
        
        if not products:
            return
        
        # Convert embeddings to numpy array
        embeddings = np.array([p.embedding for p in products], dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Add to metadata
        self.metadata.extend(products)
        
        print(f"Added {len(products)} products to vector store")
    
    def search_similar(self, query_embedding: List[float], k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar products"""
        if self.index is None:
            self._load_or_create_index()
        
        if self.index.ntotal == 0:
            print("Vector store is empty")
            return []
        
        # Convert query to numpy array
        query_array = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        
        # Search FAISS index
        distances, indices = self.index.search(query_array, min(k, self.index.ntotal))
        
        # Build results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx >= 0 and idx < len(self.metadata):
                product = self.metadata[idx]
                # Convert distance to similarity score (0-1, higher is better)
                similarity = 1 / (1 + distance)
                
                results.append({
                    'product_id': product.product_id,
                    'name': product.name,
                    'category': product.category,
                    'subcategory': product.subcategory,
                    'price_inr': product.price_inr,
                    'brand': product.brand,
                    'occasion_tags': product.occasion_tags,
                    'relationship_tags': product.relationship_tags,
                    'interest_tags': product.interest_tags,
                    'image_url': product.image_url,
                    'affiliate_link': product.affiliate_link,
                    'is_active': product.is_active,
                    'similarity_score': float(similarity),
                    'distance': float(distance),
                    'rank': i + 1
                })
        
        return results
    
    def save_index(self):
        """Save FAISS index and metadata to disk"""
        try:
            if self.index is not None:
                faiss.write_index(self.index, self.index_file)
                
                with open(self.metadata_file, 'wb') as f:
                    pickle.dump(self.metadata, f)
                
                print(f"Saved {len(self.metadata)} products to vector store")
                return True
        except Exception as e:
            print(f"Error saving index: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_products': len(self.metadata),
            'dimension': self.dimension,
            'index_type': 'FAISS IndexFlatL2',
            'index_file': self.index_file,
            'metadata_file': self.metadata_file,
            'is_empty': self.index.ntotal == 0 if self.index else True
        }
    
    def delete_index(self):
        """Delete the index files"""
        try:
            if os.path.exists(self.index_file):
                os.remove(self.index_file)
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            print("Vector store files deleted")
            return True
        except Exception as e:
            print(f"Error deleting index files: {e}")
            return False

# Sample product data for testing
def create_sample_products() -> List[ProductVector]:
    """Create sample products for testing"""
    products = [
        ProductVector(
            product_id="prod_001",
            name="Fender Guitar Strap",
            category="Music & Instruments",
            subcategory="Guitar Accessories",
            price_inr=1899.0,
            brand="Fender",
            occasion_tags=["birthday", "anniversary"],
            relationship_tags=["friend", "family"],
            interest_tags=["music", "guitar"],
            image_url="https://picsum.photos/seed/fender-strap/400/300.jpg",
            affiliate_link="https://example.com/fender-strap",
            embedding=np.random.rand(1536).tolist()  # Random embedding for testing
        ),
        ProductVector(
            product_id="prod_002",
            name="Wireless Bluetooth Headphones",
            category="Electronics",
            subcategory="Audio",
            price_inr=2499.0,
            brand="Sony",
            occasion_tags=["birthday", "graduation"],
            relationship_tags=["friend", "colleague"],
            interest_tags=["music", "technology"],
            image_url="https://picsum.photos/seed/sony-headphones/400/300.jpg",
            affiliate_link="https://example.com/sony-headphones",
            embedding=np.random.rand(1536).tolist()
        ),
        ProductVector(
            product_id="prod_003",
            name="Smart Watch",
            category="Electronics",
            subcategory="Wearables",
            price_inr=3999.0,
            brand="Apple",
            occasion_tags=["birthday", "anniversary"],
            relationship_tags=["partner", "family"],
            interest_tags=["technology", "fitness"],
            image_url="https://picsum.photos/seed/apple-watch/400/300.jpg",
            affiliate_link="https://example.com/apple-watch",
            embedding=np.random.rand(1536).tolist()
        )
    ]
    return products

# Global vector store instance
vector_store = FAISSVectorStore()

def initialize_vector_store():
    """Initialize vector store with sample data if empty"""
    if vector_store.index.ntotal == 0:
        print("Initializing vector store with sample products...")
        sample_products = create_sample_products()
        vector_store.add_products(sample_products)
        vector_store.save_index()
        print(f"Vector store initialized with {len(sample_products)} products")
    else:
        print(f"Vector store already has {vector_store.index.ntotal} products")

if __name__ == "__main__":
    # Test the vector store
    print("Testing FAISS Vector Store...")
    
    # Initialize
    initialize_vector_store()
    
    # Show stats
    stats = vector_store.get_stats()
    print(f"Vector Store Stats: {json.dumps(stats, indent=2)}")
    
    # Test search
    query_embedding = np.random.rand(1536).tolist()
    results = vector_store.search_similar(query_embedding, k=3)
    
    print(f"\nSearch Results:")
    for result in results:
        print(f"  {result['rank']}. {result['name']} - Similarity: {result['similarity_score']:.3f}")
    
    # Save
    vector_store.save_index()
    print("\nVector store test completed!")
