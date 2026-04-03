"""
Simple Vector Store - Free, No Dependencies, No Login Required
Alternative to Pinecone using basic Python with cosine similarity
"""

import os
import json
import math
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel

class ProductVector(BaseModel):
    """Product vector model for simple storage"""
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

class SimpleVectorStore:
    """Simple vector store using cosine similarity"""
    
    def __init__(self, data_file: str = "data/vector_store.json"):
        self.data_file = data_file
        self.products = []
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        
        # Load existing data or create new
        self._load_or_create_data()
    
    def _load_or_create_data(self):
        """Load existing data or create sample data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.products = [ProductVector(**item) for item in data]
                print(f"Loaded {len(self.products)} products from {self.data_file}")
            else:
                print("Creating new vector store with sample data")
                self.products = self._create_sample_products()
                self._save_data()
        except Exception as e:
            print(f"Error loading data: {e}")
            print("Creating new vector store with sample data")
            self.products = self._create_sample_products()
            self._save_data()
    
    def _create_sample_products(self) -> List[ProductVector]:
        """Create sample products"""
        # Generate simple embeddings based on product characteristics
        products = [
            ProductVector(
                product_id="prod_001",
                name="Fender Guitar Strap",
                category="Music & Instruments",
                subcategory="Guitar Accessories",
                price_inr=1899.0,
                brand="Fender",
                occasion_tags=["birthday", "anniversary", "just_because"],
                relationship_tags=["friend", "family", "partner"],
                interest_tags=["music", "guitar", "rock"],
                image_url="https://picsum.photos/seed/fender-strap/400/300.jpg",
                affiliate_link="https://example.com/fender-strap",
                embedding=self._generate_embedding(["music", "guitar", "accessories", "fender"])
            ),
            ProductVector(
                product_id="prod_002",
                name="Wireless Bluetooth Headphones",
                category="Electronics",
                subcategory="Audio",
                price_inr=2499.0,
                brand="Sony",
                occasion_tags=["birthday", "graduation", "promotion"],
                relationship_tags=["friend", "colleague", "family"],
                interest_tags=["music", "technology", "travel"],
                image_url="https://picsum.photos/seed/sony-headphones/400/300.jpg",
                affiliate_link="https://example.com/sony-headphones",
                embedding=self._generate_embedding(["music", "technology", "wireless", "audio"])
            ),
            ProductVector(
                product_id="prod_003",
                name="Smart Watch",
                category="Electronics",
                subcategory="Wearables",
                price_inr=3999.0,
                brand="Apple",
                occasion_tags=["birthday", "anniversary", "graduation"],
                relationship_tags=["partner", "family", "friend"],
                interest_tags=["technology", "fitness", "health"],
                image_url="https://picsum.photos/seed/apple-watch/400/300.jpg",
                affiliate_link="https://example.com/apple-watch",
                embedding=self._generate_embedding(["technology", "fitness", "smart", "wearable"])
            ),
            ProductVector(
                product_id="prod_004",
                name="Coffee Maker",
                category="Home & Kitchen",
                subcategory="Appliances",
                price_inr=1299.0,
                brand="Breville",
                occasion_tags=["housewarming", "wedding", "anniversary"],
                relationship_tags=["friend", "family", "colleague"],
                interest_tags=["coffee", "cooking", "home"],
                image_url="https://picsum.photos/seed/coffee-maker/400/300.jpg",
                affiliate_link="https://example.com/coffee-maker",
                embedding=self._generate_embedding(["coffee", "kitchen", "appliance", "home"])
            ),
            ProductVector(
                product_id="prod_005",
                name="Yoga Mat",
                category="Sports & Fitness",
                subcategory="Yoga",
                price_inr=799.0,
                brand="Nike",
                occasion_tags=["birthday", "health", "wellness"],
                relationship_tags=["friend", "partner", "family"],
                interest_tags=["fitness", "yoga", "health"],
                image_url="https://picsum.photos/seed/yoga-mat/400/300.jpg",
                affiliate_link="https://example.com/yoga-mat",
                embedding=self._generate_embedding(["fitness", "yoga", "sports", "exercise"])
            ),
            ProductVector(
                product_id="prod_006",
                name="Book Collection Set",
                category="Books & Media",
                subcategory="Fiction",
                price_inr=599.0,
                brand="Penguin Classics",
                occasion_tags=["birthday", "graduation", "just_because"],
                relationship_tags=["friend", "family", "colleague"],
                interest_tags=["reading", "literature", "education"],
                image_url="https://picsum.photos/seed/book-set/400/300.jpg",
                affiliate_link="https://example.com/book-set",
                embedding=self._generate_embedding(["reading", "books", "literature", "education"])
            )
        ]
        return products
    
    def _generate_embedding(self, keywords: List[str]) -> List[float]:
        """Generate simple embedding based on keywords"""
        # Create a simple 1536-dimensional embedding
        embedding = [0.0] * 1536
        
        # Map keywords to different parts of the embedding
        keyword_map = {
            "music": 0.1, "guitar": 0.2, "accessories": 0.15, "fender": 0.25,
            "technology": 0.3, "wireless": 0.2, "audio": 0.25, "sony": 0.15,
            "smart": 0.35, "wearable": 0.2, "fitness": 0.3, "apple": 0.4,
            "coffee": 0.2, "kitchen": 0.15, "appliance": 0.25, "home": 0.1,
            "fitness": 0.3, "yoga": 0.35, "sports": 0.2, "exercise": 0.25,
            "reading": 0.2, "books": 0.3, "literature": 0.25, "education": 0.15
        }
        
        # Place keyword values in different positions
        positions = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400]
        
        for i, keyword in enumerate(keywords):
            if keyword.lower() in keyword_map and i < len(positions):
                pos = positions[i]
                embedding[pos] = keyword_map[keyword.lower()]
        
        # Add some randomness to make it more realistic
        import random
        for i in range(1536):
            if embedding[i] == 0.0:
                embedding[i] = random.uniform(-0.1, 0.1)
        
        # Normalize the embedding
        magnitude = math.sqrt(sum(x*x for x in embedding))
        if magnitude > 0:
            embedding = [x/magnitude for x in embedding]
        
        return embedding
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def add_product(self, product: ProductVector):
        """Add a product to the vector store"""
        self.products.append(product)
        print(f"Added product {product.product_id} to vector store")
    
    def search_similar(self, query_embedding: List[float], k: int = 10) -> List[Dict[str, Any]]:
        """Search for similar products using cosine similarity"""
        if not self.products:
            print("Vector store is empty")
            return []
        
        # Calculate similarities
        similarities = []
        for product in self.products:
            similarity = self._cosine_similarity(query_embedding, product.embedding)
            similarities.append((product, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Build results
        results = []
        for i, (product, similarity) in enumerate(similarities[:k]):
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
                'rank': i + 1
            })
        
        return results
    
    def _save_data(self):
        """Save data to file"""
        try:
            with open(self.data_file, 'w') as f:
                data = [product.dict() for product in self.products]
                json.dump(data, f, indent=2)
            print(f"Saved {len(self.products)} products to {self.data_file}")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_products': len(self.products),
            'dimension': 1536,
            'storage_type': 'JSON File',
            'data_file': self.data_file,
            'similarity_metric': 'Cosine Similarity',
            'is_empty': len(self.products) == 0
        }
    
    def delete_store(self):
        """Delete the data file"""
        try:
            if os.path.exists(self.data_file):
                os.remove(self.data_file)
            print("Vector store data file deleted")
            return True
        except Exception as e:
            print(f"Error deleting data file: {e}")
            return False

# Global vector store instance
simple_vector_store = SimpleVectorStore()

def initialize_simple_vector_store():
    """Initialize vector store"""
    if not simple_vector_store.products:
        print("Vector store is empty, creating sample data...")
        simple_vector_store.products = simple_vector_store._create_sample_products()
        simple_vector_store._save_data()
    else:
        print(f"Vector store has {len(simple_vector_store.products)} products")

if __name__ == "__main__":
    # Test the simple vector store
    print("Testing Simple Vector Store...")
    
    # Show stats
    stats = simple_vector_store.get_stats()
    print(f"Vector Store Stats: {json.dumps(stats, indent=2)}")
    
    # Test search
    query_embedding = simple_vector_store._generate_embedding(["music", "guitar"])
    results = simple_vector_store.search_similar(query_embedding, k=3)
    
    print(f"\nSearch Results:")
    for result in results:
        print(f"  {result['rank']}. {result['name']} - Similarity: {result['similarity_score']:.3f}")
    
    print("\nSimple Vector Store test completed!")
