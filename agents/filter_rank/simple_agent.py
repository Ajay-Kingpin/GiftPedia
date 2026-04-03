"""
Agent 3: Filter & Rank (Simple Version)
Filters and ranks products based on user profile and creative concepts using simple vector store
"""

import os
import json
import math
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

from agents.profile_analyzer import UserProfile
from agents.creative_idea import GiftConcept
from services.simple_vector_store import SimpleVectorStore, ProductVector, simple_vector_store, initialize_simple_vector_store

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
    """Filters and ranks products based on user profile and concepts using simple vector store"""
    
    def __init__(self):
        # Initialize simple vector store
        self.vector_store = simple_vector_store
        initialize_simple_vector_store()
        
        # Load product catalog
        self.product_catalog = self._load_product_catalog()
        
        print(f"Simple Filter & Rank Agent initialized with {len(self.product_catalog)} products")
    
    def _load_product_catalog(self) -> List[Product]:
        """Load product catalog from vector store"""
        products = []
        for product_vector in self.vector_store.products:
            product = Product(
                product_id=product_vector.product_id,
                name=product_vector.name,
                category=product_vector.category,
                subcategory=product_vector.subcategory,
                price_inr=product_vector.price_inr,
                brand=product_vector.brand,
                occasion_tags=product_vector.occasion_tags,
                relationship_tags=product_vector.relationship_tags,
                interest_tags=product_vector.interest_tags,
                image_url=product_vector.image_url,
                affiliate_link=product_vector.affiliate_link,
                is_active=product_vector.is_active
            )
            products.append(product)
        
        print(f"Loaded {len(products)} products from vector store")
        return products
    
    def filter_by_budget(self, products: List[Product], budget: float) -> List[Product]:
        """Filter products by budget"""
        filtered = [p for p in products if p.price_inr <= budget * 1.2]  # Allow 20% flexibility
        print(f"Budget filter: {len(products)} -> {len(filtered)} products (budget: ₹{budget})")
        return filtered
    
    def filter_by_interests(self, products: List[Product], interests: List[str]) -> List[Product]:
        """Filter products by interests"""
        if not interests:
            return products
        
        interests_lower = [interest.lower() for interest in interests]
        scored_products = []
        
        for product in products:
            score = 0
            product_tags = [tag.lower() for tag in product.interest_tags + product.occasion_tags + product.relationship_tags]
            
            for interest in interests_lower:
                for tag in product_tags:
                    if interest in tag or tag in interest:
                        score += 1
            
            if score > 0:
                scored_products.append((product, score))
        
        # Sort by relevance score
        scored_products.sort(key=lambda x: x[1], reverse=True)
        filtered = [product for product, score in scored_products]
        
        print(f"Interest filter: {len(products)} -> {len(filtered)} products (interests: {interests})")
        return filtered
    
    def filter_by_occasion(self, products: List[Product], occasion: str) -> List[Product]:
        """Filter products by occasion"""
        if not occasion or occasion == "other":
            return products
        
        occasion_lower = occasion.lower()
        filtered = []
        
        for product in products:
            product_occasions = [tag.lower() for tag in product.occasion_tags]
            if occasion_lower in product_occasions or "just_because" in product_occasions:
                filtered.append(product)
        
        print(f"Occasion filter: {len(products)} -> {len(filtered)} products (occasion: {occasion})")
        return filtered
    
    def filter_by_relationship(self, products: List[Product], relationship: str) -> List[Product]:
        """Filter products by relationship"""
        if not relationship or relationship == "other":
            return products
        
        relationship_lower = relationship.lower()
        filtered = []
        
        for product in products:
            product_relationships = [tag.lower() for tag in product.relationship_tags]
            if relationship_lower in product_relationships or "friend" in product_relationships:
                filtered.append(product)
        
        print(f"Relationship filter: {len(products)} -> {len(filtered)} products (relationship: {relationship})")
        return filtered
    
    def calculate_relevance_score(self, product: Product, profile: UserProfile, concepts: List[GiftConcept]) -> float:
        """Calculate relevance score for a product"""
        score = 0.0
        
        # Budget alignment (0-0.3)
        if product.price_inr <= profile.budget_inr:
            score += 0.3
        elif product.price_inr <= profile.budget_inr * 1.2:
            score += 0.15
        
        # Interest alignment (0-0.4)
        interest_matches = 0
        for interest in profile.interests:
            for tag in product.interest_tags:
                if interest.lower() in tag.lower() or tag.lower() in interest.lower():
                    interest_matches += 1
        score += min(interest_matches * 0.1, 0.4)
        
        # Occasion alignment (0-0.2)
        if profile.occasion != "other":
            occasion_lower = profile.occasion.lower()
            for tag in product.occasion_tags:
                if occasion_lower in tag.lower():
                    score += 0.2
                    break
        
        # Relationship alignment (0-0.1)
        if profile.relationship != "other":
            relationship_lower = profile.relationship.lower()
            for tag in product.relationship_tags:
                if relationship_lower in tag.lower():
                    score += 0.1
                    break
        
        return score
    
    def semantic_search(self, query_embedding: List[float], k: int = 20) -> List[Dict[str, Any]]:
        """Perform semantic search using simple vector store"""
        try:
            results = self.vector_store.search_similar(query_embedding, k=k)
            return results
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []
    
    def filter_and_rank_products(self, profile: UserProfile, concepts: List[GiftConcept], 
                             query_embedding: Optional[List[float]] = None,
                             max_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Main method to filter and rank products"""
        print(f"🎁 Filtering and ranking products for {profile.relationship} gift")
        
        # Start with semantic search if embedding is provided
        if query_embedding:
            semantic_results = self.semantic_search(query_embedding, k=50)
            candidate_products = []
            
            # Convert semantic results to Product objects
            for result in semantic_results:
                if result['similarity_score'] > 0.2:  # Minimum similarity threshold
                    product = Product(
                        product_id=result['product_id'],
                        name=result['name'],
                        category=result['category'],
                        subcategory=result['subcategory'],
                        price_inr=result['price_inr'],
                        brand=result['brand'],
                        occasion_tags=result['occasion_tags'],
                        relationship_tags=result['relationship_tags'],
                        interest_tags=result['interest_tags'],
                        image_url=result['image_url'],
                        affiliate_link=result['affiliate_link'],
                        is_active=result['is_active']
                    )
                    candidate_products.append(product)
            
            print(f"Semantic search found {len(candidate_products)} candidate products")
        else:
            candidate_products = self.product_catalog.copy()
        
        # Apply filters
        filtered_products = candidate_products
        
        # Budget filter
        filtered_products = self.filter_by_budget(filtered_products, profile.budget_inr)
        
        # Interest filter
        filtered_products = self.filter_by_interests(filtered_products, profile.interests)
        
        # Occasion filter
        filtered_products = self.filter_by_occasion(filtered_products, profile.occasion)
        
        # Relationship filter
        filtered_products = self.filter_by_relationship(filtered_products, profile.relationship)
        
        # Calculate final scores
        scored_products = []
        for product in filtered_products:
            relevance_score = self.calculate_relevance_score(product, profile, concepts)
            
            # Get semantic similarity if available
            semantic_score = 0.0
            if query_embedding:
                for result in semantic_results:
                    if result['product_id'] == product.product_id:
                        semantic_score = result['similarity_score']
                        break
            
            # Combine scores (70% relevance, 30% semantic)
            final_score = (relevance_score * 0.7) + (semantic_score * 0.3)
            
            scored_products.append({
                'product': product,
                'relevance_score': relevance_score,
                'semantic_score': semantic_score,
                'final_score': final_score
            })
        
        # Sort by final score
        scored_products.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Limit results
        top_products = scored_products[:max_recommendations]
        
        # Format results
        recommendations = []
        for i, item in enumerate(top_products):
            product = item['product']
            
            recommendations.append({
                'product_id': product.product_id,
                'name': product.name,
                'category': product.category,
                'subcategory': product.subcategory,
                'price_inr': product.price_inr,
                'brand': product.brand,
                'image_url': product.image_url,
                'affiliate_link': product.affiliate_link,
                'interest_tags': product.interest_tags,
                'occasion_tags': product.occasion_tags,
                'relationship_tags': product.relationship_tags,
                'relevance_score': item['relevance_score'],
                'semantic_score': item['semantic_score'],
                'final_score': item['final_score'],
                'rank': i + 1
            })
        
        print(f"✅ Generated {len(recommendations)} ranked recommendations")
        return recommendations

# Global agent instance
filter_rank_agent = FilterRankAgent()

if __name__ == "__main__":
    # Test the Simple Filter & Rank Agent
    print("Testing Simple Filter & Rank Agent...")
    
    # Create test profile
    test_profile = UserProfile(
        recipient_age=28,
        recipient_gender="male",
        interests=["music", "guitar"],
        relationship="family",
        occasion="birthday",
        budget_inr=2000,
        constraints=["no plastic"]
    )
    
    # Create test concepts
    test_concepts = [
        GiftConcept(
            concept="Music accessories for guitar enthusiasts",
            category="Music",
            reasoning="Perfect for someone who loves playing guitar"
        )
    ]
    
    # Test filtering and ranking
    recommendations = filter_rank_agent.filter_and_rank_products(
        test_profile, test_concepts, max_recommendations=5
    )
    
    print(f"\nTop Recommendations:")
    for rec in recommendations:
        print(f"  {rec['rank']}. {rec['name']} - ₹{rec['price_inr']} (Score: {rec['final_score']:.3f})")
    
    print("\nSimple Filter & Rank Agent test completed!")
