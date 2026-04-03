"""
Simple FastAPI Server - Works without external API dependencies
For manual testing of the GiftPedia frontend
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models
class RecommendationRequest(BaseModel):
    user_input: str = Field(..., description="User's gift request")
    max_recommendations: int = Field(default=10, description="Maximum recommendations to return")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")

class RecommendationExplanation(BaseModel):
    product_id: str
    product_name: str
    explanation: str
    key_reasons: List[str]
    confidence_score: float
    match_factors: List[str]

class RecommendationResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

# Sample product data with diverse categories and features
SAMPLE_PRODUCTS = [
    {
        "product_id": "prod_001",
        "name": "Wireless Bluetooth Headphones",
        "category": "Electronics",
        "subcategory": "Audio",
        "brand": "Sony",
        "price": 4999,
        "currency": "INR",
        "availability": "In Stock",
        "image_url": "https://picsum.photos/seed/headphones123/400/300.jpg",
        "description": "Premium wireless headphones with noise cancellation",
        "features": ["Wireless", "Noise Cancelling", "Bluetooth", "Music"],
        "specifications": {"battery_life": "30 hours", "weight": "250g"},
        "tags": ["electronics", "music", "audio"],
        "affiliate_url": "https://amazon.in/dp/B08N5M8X5K?tag=giftpedia-test-20"
    },
    {
        "product_id": "prod_002",
        "name": "Professional Kitchen Knife Set",
        "category": "Kitchen",
        "subcategory": "Cookware",
        "brand": "Prestige",
        "price": 2999,
        "currency": "INR",
        "availability": "In Stock",
        "image_url": "https://picsum.photos/seed/knife456/400/300.jpg",
        "description": "Professional stainless steel knife set with wooden block",
        "features": ["Stainless Steel", "Professional", "Sharp", "Cooking"],
        "specifications": {"pieces": "6", "material": "Stainless Steel"},
        "tags": ["kitchen", "cooking", "utensils"],
        "affiliate_url": "https://amazon.in/dp/B08N5M8X5K?tag=giftpedia-test-20"
    },
    {
        "product_id": "prod_003",
        "name": "Silk Scarf with Floral Pattern",
        "category": "Fashion",
        "subcategory": "Accessories",
        "brand": "FabIndia",
        "price": 1299,
        "currency": "INR",
        "availability": "In Stock",
        "image_url": "https://picsum.photos/seed/scarf789/400/300.jpg",
        "description": "Elegant silk scarf with beautiful floral pattern",
        "features": ["Silk", "Floral", "Elegant", "Fashion"],
        "specifications": {"material": "100% Silk", "size": "180x70 cm"},
        "tags": ["fashion", "accessories", "gift"],
        "affiliate_url": "https://amazon.in/dp/B08N5M8X5K?tag=giftpedia-test-20"
    },
    {
        "product_id": "prod_004",
        "name": "Smart Home Security Camera",
        "category": "Electronics",
        "subcategory": "Security",
        "brand": "Mi",
        "price": 3499,
        "currency": "INR",
        "availability": "In Stock",
        "image_url": "https://picsum.photos/seed/camera234/400/300.jpg",
        "description": "WiFi security camera with night vision and mobile app",
        "features": ["WiFi", "Night Vision", "Mobile App", "Security"],
        "specifications": {"resolution": "1080p", "storage": "Cloud", "viewing_angle": "360°"},
        "tags": ["electronics", "home", "security", "smart"],
        "affiliate_url": "https://amazon.in/dp/B08N5M8X5K?tag=giftpedia-test-20"
    },
    {
        "product_id": "prod_005",
        "name": "Yoga Mat with Carrying Strap",
        "category": "Sports",
        "subcategory": "Fitness",
        "brand": "Nike",
        "price": 1999,
        "currency": "INR",
        "availability": "In Stock",
        "image_url": "https://picsum.photos/seed/yoga567/400/300.jpg",
        "description": "Non-slip yoga mat with carrying strap and alignment marks",
        "features": ["Non-slip", "Eco-friendly", "Portable", "Yoga"],
        "specifications": {"thickness": "6mm", "material": "TPE", "size": "183x61 cm"},
        "tags": ["sports", "fitness", "yoga", "exercise"],
        "affiliate_url": "https://amazon.in/dp/B08N5M8X5K?tag=giftpedia-test-20"
    },
    {
        "product_id": "prod_006",
        "name": "Luxury Skincare Gift Set",
        "category": "Beauty",
        "subcategory": "Skincare",
        "brand": "Forest Essentials",
        "price": 2499,
        "currency": "INR",
        "availability": "In Stock",
        "image_url": "https://picsum.photos/seed/skincare890/400/300.jpg",
        "description": "Complete skincare set with face wash, toner, and moisturizer",
        "features": ["Natural", "Anti-aging", "Moisturizing", "Beauty"],
        "specifications": {"items": "3", "skin_type": "All Skin Types", "organic": True},
        "tags": ["beauty", "skincare", "natural", "gift Set"],
        "affiliate_url": "https://amazon.in/dp/B08N5M8X5K?tag=giftpedia-test-20"
    },
    {
        "product_id": "prod_007",
        "name": "Bestselling Novel Collection",
        "category": "Books",
        "subcategory": "Fiction",
        "brand": "Penguin Classics",
        "price": 1599,
        "currency": "INR",
        "availability": "In Stock",
        "image_url": "https://picsum.photos/seed/books345/400/300.jpg",
        "description": "Collection of bestselling novels including mystery, romance, and thriller",
        "features": ["Bestselling", "Multiple Genres", "Gift Box", "Books"],
        "specifications": {"books": "5", "format": "Paperback", "language": "English"},
        "tags": ["books", "fiction", "bestseller", "collection"],
        "affiliate_url": "https://amazon.in/dp/B08N5M8X5K?tag=giftpedia-test-20"
    },
    {
        "product_id": "prod_008",
        "name": "Educational Building Blocks Set",
        "category": "Toys",
        "subcategory": "Educational",
        "brand": "Lego",
        "price": 3499,
        "currency": "INR",
        "availability": "In Stock",
        "image_url": "https://picsum.photos/seed/blocks678/400/300.jpg",
        "description": "Educational building blocks that promote creativity and learning",
        "features": ["Educational", "Creative", "STEM", "Building"],
        "specifications": {"pieces": "500", "age_range": "6-12 years", "material": "Plastic"},
        "tags": ["toys", "educational", "STEM", "building"],
        "affiliate_url": "https://amazon.in/dp/B08N5M8X5K?tag=giftpedia-test-20"
    }
]

class SimpleGiftRecommendationService:
    """Simple recommendation service for testing"""
    
    def __init__(self):
        self.products = SAMPLE_PRODUCTS
        logger.info("Simple Gift Recommendation Service initialized")
    
    def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """Get gift recommendations"""
        start_time = datetime.now()
        session_id = request.session_id or f"session_{int(start_time.timestamp())}"
        
        try:
            # Simple keyword-based filtering
            user_input_lower = request.user_input.lower()
            filtered_products = []
            
            for product in self.products:
                score = 0
                
                # Check interest matches
                for tag in product.get("tags", []):
                    if tag in user_input_lower:
                        score += 2
                
                
                # Check category matches
                if product["category"].lower() in user_input_lower:
                    score += 1
                
                if score > 0:
                    filtered_products.append({
                        **product,
                        "relevance_score": score,
                        "final_score": min(score / 5.0, 1.0)  # Normalize to 0-1
                    })
            
            # Sort by score
            filtered_products.sort(key=lambda x: x["final_score"], reverse=True)
            
            # Limit results
            top_products = filtered_products[:request.max_recommendations]
            
            # Generate explanations
            explanations = []
            for i, product in enumerate(top_products):
                explanation = self._generate_explanation(product, request.user_input)
                explanations.append(explanation)
            
            # Create response
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            response = RecommendationResponse(
                success=True,
                data={
                    "profile": {
                        "recipient_age": 28,
                        "recipient_gender": "unknown",
                        "interests": self._extract_interests(request.user_input),
                        "relationship": self._extract_relationship(request.user_input),
                        "occasion": self._extract_occasion(request.user_input),
                        "budget_inr": self._extract_budget(request.user_input),
                        "constraints": []
                    },
                    "concepts": [
                        {
                            "concept": self._extract_main_concept(request.user_input),
                            "category": "General",
                            "reasoning": "Based on user input analysis"
                        }
                    ],
                    "recommendations": top_products,
                    "explanations": explanations,
                    "summary": f"Found {len(top_products)} personalized gift recommendations based on your request."
                },
                processing_time=processing_time,
                session_id=session_id,
                timestamp=end_time.isoformat()
            )
            
            logger.info(f"Generated {len(top_products)} recommendations in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return RecommendationResponse(
                success=False,
                error=str(e),
                processing_time=processing_time,
                session_id=session_id,
                timestamp=end_time.isoformat()
            )
    
    def _generate_explanation(self, product: Dict[str, Any], user_input: str) -> RecommendationExplanation:
        """Generate explanation for a product"""
        return RecommendationExplanation(
            product_id=product["product_id"],
            product_name=product["name"],
            explanation=f"This {product['name']} is an excellent choice that matches the recipient's interests and your specified occasion. It offers great value and thoughtful features.",
            key_reasons=[
                f"Perfect for {product.get('tags', [])[0] if product.get('tags', []) else 'their'} interests",
                f"Great for {product.get('tags', [])[1] if len(product.get('tags', [])) > 1 else 'any'} occasions",
                f"High-quality {product.get('brand', 'Unknown')} product",
                f"Good value at ₹{product.get('price', '0')}"
            ],
            confidence_score=product.get("final_score", 0.8),
            match_factors=["Interest alignment", "Quality", "Value", "Occasion appropriate"]
        )
    
    def _extract_interests(self, user_input: str) -> List[str]:
        """Extract interests from user input"""
        interests = []
        interest_keywords = ["music", "guitar", "technology", "fitness", "yoga", "coffee", "books", "travel"]
        for keyword in interest_keywords:
            if keyword in user_input.lower():
                interests.append(keyword)
        return interests or ["general"]
    
    def _extract_relationship(self, user_input: str) -> str:
        """Extract relationship from user input"""
        relationship_keywords = {
            "brother": "family",
            "sister": "family",
            "friend": "friend",
            "husband": "partner",
            "wife": "partner",
            "father": "family",
            "mother": "family"
        }
        for keyword, rel in relationship_keywords.items():
            if keyword in user_input.lower():
                return rel
        return "other"
    
    def _extract_occasion(self, user_input: str) -> str:
        """Extract occasion from user input"""
        occasion_keywords = {
            "birthday": "birthday",
            "anniversary": "anniversary",
            "graduation": "graduation",
            "wedding": "wedding",
            "housewarming": "housewarming"
        }
        for keyword, occ in occasion_keywords.items():
            if keyword in user_input.lower():
                return occ
        return "other"
    
    def _extract_budget(self, user_input: str) -> float:
        """Extract budget from user input"""
        import re
        # Look for numbers followed by currency symbols
        patterns = [
            r'₹(\d+)',
            r'budget\s*(?:of\s*)?(\d+)',
            r'(\d+)\s*(?:rupees|rs)'
        ]
        for pattern in patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                return float(match.group(1))
        return 2000.0  # Default budget
    
    def _extract_main_concept(self, user_input: str) -> str:
        """Extract main concept from user input"""
        if "music" in user_input.lower():
            return "Music-related gifts"
        elif "technology" in user_input.lower():
            return "Technology gadgets"
        elif "fitness" in user_input.lower():
            return "Fitness equipment"
        elif "coffee" in user_input.lower():
            return "Coffee accessories"
        else:
            return "General gift recommendations"

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.recommendation_service = SimpleGiftRecommendationService()
    logger.info("API server started successfully")
    yield
    # Shutdown
    logger.info("API server shutting down")

app = FastAPI(
    title="GiftPedia API",
    description="Gift Recommendation API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"message": "GiftPedia API is running", "version": "1.0.0"}

@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "service": "GiftPedia API"
    }

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get gift recommendations"""
    service = app.state.recommendation_service
    return service.get_recommendations(request)

@app.get("/categories", response_model=List[Dict[str, Any]])
async def get_categories():
    """Get available product categories"""
    categories = {}
    for product in SAMPLE_PRODUCTS:
        category = product["category"]
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    return [
        {"id": cat, "name": cat, "product_count": count}
        for cat, count in categories.items()
    ]

@app.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product_details(product_id: str):
    """Get product details by ID"""
    for product in SAMPLE_PRODUCTS:
        if product["product_id"] == product_id:
            return product
    
    raise HTTPException(status_code=404, detail="Product not found")

@app.get("/popular-gifts", response_model=List[Dict[str, Any]])
async def get_popular_gifts(category: Optional[str] = None, limit: int = 10):
    """Get popular gifts"""
    products = SAMPLE_PRODUCTS.copy()
    
    if category:
        products = [p for p in products if p["category"] == category]
    
    return products[:limit]

if __name__ == "__main__":
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
