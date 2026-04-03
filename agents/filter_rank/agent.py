"""
Agent 3: Filter & Rank (Deterministic)
Filters and ranks products based on user profile and creative concepts
"""

import os
import json
import pinecone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import numpy as np

from agents.profile_analyzer import UserProfile
from agents.creative_idea import GiftConcept

class Product(BaseModel):
    """Product model for filtering and ranking"""
    product_id: str = Field(description="Unique product identifier")
    name: str = Field(description="Product name")
    category: str = Field(description="Product category")
    subcategory: str = Field(description="Product subcategory")
    price_inr: float = Field(description="Price in Indian Rupees")
    brand: str = Field(description="Product brand")
    occasion_tags: List[str] = Field(default_factory=list, description="Occasion tags")
    relationship_tags: List[str] = Field(default_factory=list, description="Relationship tags")
    interest_tags: List[str] = Field(default_factory=list, description="Interest tags")
    image_url: Optional[str] = Field(None, description="Product image URL")
    affiliate_link: Optional[str] = Field(None, description="Affiliate link")
    is_active: bool = Field(True, description="Product availability status")
    embedding: Optional[List[float]] = Field(None, description="Product embedding vector")

class FilterRankAgent:
    """Filters and ranks products based on user profile and concepts"""
    
    def __init__(self):
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        environment = os.getenv("PINECONE_ENVIRONMENT", "us-west1-gcp")
        index_name = os.getenv("PINECONE_INDEX_NAME", "giftpedia_products_v1")
        
        # Initialize Pinecone client (older API)
        pinecone.init(api_key=api_key, environment=environment)
        
        # Connect to index
        if index_name not in pinecone.list_indexes():
            raise ValueError(f"Pinecone index '{index_name}' not found")
        
        self.index = pinecone.Index(index_name)
        
        # Embedding dimensions (Google text-embedding-004)
        self.embedding_dim = 1536
        
    def generate_search_query(self, profile: UserProfile, concepts: List[GiftConcept]) -> str:
        """
        Generate search query from profile and concepts
        
        Args:
            profile: User profile
            concepts: Creative gift concepts
            
        Returns:
            Search query string
        """
        # Combine interests and concepts for better search
        interests = " ".join(profile.interests) if profile.interests else ""
        concept_keywords = []
        
        for concept in concepts:
            # Extract keywords from concept description
            keywords = concept.concept.lower().split()
            concept_keywords.extend(keywords[:3])  # Take first 3 keywords
        
        # Build search query
        query_parts = []
        if interests:
            query_parts.append(interests)
        if concept_keywords:
            query_parts.append(" ".join(concept_keywords))
        if profile.recipient_gender != "unknown":
            query_parts.append(profile.recipient_gender)
        
        return " ".join(query_parts)
    
    def search_similar_products(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Search for similar products using vector similarity
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of similar products with metadata
        """
        try:
            # Generate embedding for query (mock implementation)
            # In real implementation, use Google text-embedding-004
            query_embedding = self._mock_embedding(query)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Convert to product objects
            products = []
            for match in results['matches']:
                metadata = match['metadata']
                product = Product(
                    product_id=match['id'],
                    name=metadata.get('name', ''),
                    category=metadata.get('category', ''),
                    subcategory=metadata.get('subcategory', ''),
                    price_inr=metadata.get('price_inr', 0.0),
                    brand=metadata.get('brand', ''),
                    occasion_tags=metadata.get('occasion_tags', []),
                    relationship_tags=metadata.get('relationship_tags', []),
                    interest_tags=metadata.get('interest_tags', []),
                    image_url=metadata.get('image_url'),
                    affiliate_link=metadata.get('affiliate_link'),
                    is_active=metadata.get('is_active', True),
                    embedding=match.get('values')
                )
                products.append({
                    'product': product,
                    'similarity_score': match['score']
                })
            
            return products
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def filter_by_budget(self, products: List[Dict[str, Any]], budget: Optional[int]) -> List[Dict[str, Any]]:
        """
        Filter products by budget
        
        Args:
            products: List of products with similarity scores
            budget: Maximum budget in INR
            
        Returns:
            Filtered products
        """
        if budget is None:
            return products
        
        filtered = []
        for item in products:
            product = item['product']
            if product.price_inr <= budget:
                filtered.append(item)
        
        return filtered
    
    def filter_by_constraints(self, products: List[Dict[str, Any]], constraints: List[str]) -> List[Dict[str, Any]]:
        """
        Filter products by user constraints
        
        Args:
            products: List of products with similarity scores
            constraints: User constraints (e.g., "no plastic", "eco-friendly")
            
        Returns:
            Filtered products
        """
        if not constraints:
            return products
        
        filtered = []
        for item in products:
            product = item['product']
            
            # Check if product violates any constraints
            violates_constraint = False
            for constraint in constraints:
                constraint_lower = constraint.lower()
                
                # Simple constraint checking (can be enhanced)
                if 'plastic' in constraint_lower and 'plastic' in product.name.lower():
                    violates_constraint = True
                    break
                elif 'eco' in constraint_lower and 'plastic' in product.name.lower():
                    violates_constraint = True
                    break
            
            if not violates_constraint:
                filtered.append(item)
        
        return filtered
    
    def rank_products(self, products: List[Dict[str, Any]], profile: UserProfile) -> List[Dict[str, Any]]:
        """
        Rank products based on multiple factors
        
        Args:
            products: List of products with similarity scores
            profile: User profile
            
        Returns:
            Ranked products
        """
        for item in products:
            product = item['product']
            
            # Base score from similarity
            final_score = item['similarity_score']
            
            # Budget alignment bonus
            if profile.budget_inr:
                budget_ratio = product.price_inr / profile.budget_inr
                if budget_ratio <= 0.5:  # Well under budget
                    final_score += 0.1
                elif budget_ratio <= 0.8:  # Good value
                    final_score += 0.05
                elif budget_ratio > 1.0:  # Over budget
                    final_score -= 0.2
            
            # Interest alignment bonus
            interest_matches = len(set(profile.interests) & set(product.interest_tags))
            if interest_matches > 0:
                final_score += 0.05 * interest_matches
            
            # Occasion alignment bonus
            if profile.occasion in product.occasion_tags:
                final_score += 0.1
            
            # Relationship alignment bonus
            if profile.relationship in product.relationship_tags:
                final_score += 0.05
            
            # Update final score
            item['final_score'] = final_score
        
        # Sort by final score
        ranked = sorted(products, key=lambda x: x['final_score'], reverse=True)
        
        return ranked
    
    def filter_and_rank(self, profile: UserProfile, concepts: List[GiftConcept]) -> List[Dict[str, Any]]:
        """
        Main method to filter and rank products
        
        Args:
            profile: User profile
            concepts: Creative gift concepts
            
        Returns:
            Filtered and ranked products
        """
        # Generate search query
        query = self.generate_search_query(profile, concepts)
        
        # Search similar products
        products = self.search_similar_products(query)
        
        # Filter by budget
        products = self.filter_by_budget(products, profile.budget_inr)
        
        # Filter by constraints
        products = self.filter_by_constraints(products, profile.constraints)
        
        # Rank products
        ranked_products = self.rank_products(products, profile)
        
        return ranked_products
    
    def _mock_embedding(self, text: str) -> List[float]:
        """
        Mock embedding generation (replace with actual Google text-embedding-004)
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        # Simple mock: create deterministic vector based on text hash
        import hashlib
        
        hash_obj = hashlib.md5(text.encode())
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

# Singleton instance
filter_rank_agent = FilterRankAgent()

if __name__ == "__main__":
    # Test the agent
    from agents.profile_analyzer import UserProfile
    from agents.creative_idea import GiftConcept
    
    # Mock profile
    profile = UserProfile(
        recipient_age=28,
        recipient_gender="male",
        interests=["music", "guitar"],
        relationship="family",
        occasion="birthday",
        budget_inr=2000,
        constraints=[]
    )
    
    # Mock concepts
    concepts = [
        GiftConcept(
            concept="Custom guitar accessories",
            category="Music",
            reasoning="Perfect for music enthusiast"
        )
    ]
    
    # Test filtering and ranking
    agent = FilterRankAgent()
    results = agent.filter_and_rank(profile, concepts)
    
    print("Filter & Rank Test Results:")
    print("=" * 50)
    print(f"Found {len(results)} products")
    
    for i, item in enumerate(results[:5], 1):
        product = item['product']
        print(f"{i}. {product.name}")
        print(f"   Price: ₹{product.price_inr}")
        print(f"   Similarity: {item['similarity_score']:.3f}")
        print(f"   Final Score: {item['final_score']:.3f}")
        print("-" * 30)
