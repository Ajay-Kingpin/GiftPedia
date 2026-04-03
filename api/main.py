"""
FastAPI Main Server
REST API endpoints for GiftPedia frontend
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from orchestration import GiftRecommendationOrchestrator, RecommendationRequest, RecommendationResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator
    
    # Startup
    logger.info("Starting GiftPedia API server...")
    orchestrator = GiftRecommendationOrchestrator()
    logger.info("GiftPedia API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down GiftPedia API server...")

# Pydantic models for API
class GiftRecommendationRequest(BaseModel):
    """API request model for gift recommendations"""
    user_input: str = Field(..., min_length=10, max_length=1000, description="User's gift request")
    session_id: Optional[str] = Field(None, description="Session identifier")
    max_recommendations: int = Field(5, ge=1, le=10, description="Maximum number of recommendations")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="Additional user preferences")

class GiftRecommendationResponse(BaseModel):
    """API response model for gift recommendations"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None
    session_id: Optional[str] = None
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    agents: Dict[str, Dict[str, Any]]
    timestamp: str
    performance_metrics: Dict[str, Any]

# Create FastAPI app
app = FastAPI(
    title="GiftPedia API",
    description="AI-powered gift recommendation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Dependency to get orchestrator
def get_orchestrator() -> GiftRecommendationOrchestrator:
    """Get orchestrator instance"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Service not available")
    return orchestrator

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GiftPedia API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check(orch: GiftRecommendationOrchestrator = Depends(get_orchestrator)):
    """Health check endpoint"""
    try:
        health_status = orch.health_check()
        return HealthResponse(**health_status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/recommendations", response_model=GiftRecommendationResponse)
async def get_recommendations(
    request: GiftRecommendationRequest,
    background_tasks: BackgroundTasks,
    orch: GiftRecommendationOrchestrator = Depends(get_orchestrator)
):
    """
    Get gift recommendations based on user input
    
    Args:
        request: Gift recommendation request
        background_tasks: Background tasks for logging
        orch: Orchestrator instance
        
    Returns:
        Gift recommendations with explanations
    """
    try:
        logger.info(f"Processing recommendation request: {request.user_input[:100]}...")
        
        # Create recommendation request
        rec_request = RecommendationRequest(
            user_input=request.user_input,
            session_id=request.session_id,
            user_preferences=request.user_preferences,
            max_recommendations=request.max_recommendations
        )
        
        # Process request
        response = orch.get_recommendations(rec_request)
        
        # Log in background
        background_tasks.add_task(
            log_recommendation_request,
            request.user_input,
            response.session_id,
            response.processing_time,
            len(response.recommendations)
        )
        
        # Prepare response data
        response_data = {
            "profile": response.profile.dict(),
            "concepts": [concept.dict() for concept in response.concepts],
            "recommendations": response.recommendations,
            "explanations": [explanation.dict() for explanation in response.explanations],
            "summary": response.summary,
            "metadata": response.metadata
        }
        
        return GiftRecommendationResponse(
            success=True,
            data=response_data,
            processing_time=response.processing_time,
            session_id=response.session_id,
            timestamp=response.timestamp.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing recommendation request: {e}")
        return GiftRecommendationResponse(
            success=False,
            error=str(e),
            timestamp=datetime.now().isoformat()
        )

@app.get("/products/{product_id}")
async def get_product_details(product_id: str):
    """Get detailed information about a specific product"""
    try:
        # Mock product details for now
        mock_products = {
            "prod_001": {
                "product_id": "prod_001",
                "name": "Fender Guitar Strap",
                "category": "Music & Instruments",
                "subcategory": "Guitar Accessories",
                "price_inr": 1899.0,
                "brand": "Fender",
                "image_url": "https://picsum.photos/seed/prod_001/400/300.jpg",
                "affiliate_link": "https://example.com/affiliate/prod_001",
                "description": "Premium leather guitar strap with adjustable length and comfortable padding.",
                "specifications": {
                    "Material": "Genuine Leather",
                    "Length": "Adjustable 38-60 inches",
                    "Width": "2.5 inches",
                    "Padding": "Memory foam",
                    "Colors": "Black, Brown, Tan"
                },
                "reviews": [
                    {
                        "rating": 5,
                        "comment": "Best guitar strap I've ever used!",
                        "author": "John D.",
                        "date": "2024-01-15"
                    }
                ]
            }
        }
        
        if product_id not in mock_products:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return mock_products[product_id]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/categories")
async def get_categories():
    """Get available product categories"""
    categories = [
        {"id": "electronics", "name": "Electronics", "product_count": 150},
        {"id": "clothing", "name": "Clothing & Accessories", "product_count": 200},
        {"id": "home", "name": "Home & Garden", "product_count": 120},
        {"id": "sports", "name": "Sports & Outdoors", "product_count": 80},
        {"id": "books", "name": "Books & Media", "product_count": 300},
        {"id": "toys", "name": "Toys & Games", "product_count": 100},
        {"id": "beauty", "name": "Beauty & Personal Care", "product_count": 90},
        {"id": "food", "name": "Food & Gourmet", "product_count": 60}
    ]
    
    return categories

@app.get("/popular-gifts")
async def get_popular_gifts(category: Optional[str] = None, limit: int = 10):
    """Get popular gift recommendations"""
    # Mock popular gifts
    popular_gifts = [
        {
            "product_id": "prod_001",
            "name": "Fender Guitar Strap",
            "category": "Music & Instruments",
            "price_inr": 1899.0,
            "image_url": "https://picsum.photos/seed/prod_001/200/200.jpg",
            "popularity_score": 0.95
        },
        {
            "product_id": "prod_002",
            "name": "Wireless Headphones",
            "category": "Electronics",
            "price_inr": 2999.0,
            "image_url": "https://picsum.photos/seed/prod_002/200/200.jpg",
            "popularity_score": 0.92
        }
    ]
    
    if category:
        popular_gifts = [g for g in popular_gifts if g["category"].lower().find(category.lower()) != -1]
    
    return popular_gifts[:limit]

@app.get("/metrics")
async def get_metrics(orch: GiftRecommendationOrchestrator = Depends(get_orchestrator)):
    """Get system performance metrics"""
    try:
        return orch.get_performance_metrics()
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

async def log_recommendation_request(user_input: str, session_id: str, 
                                  processing_time: float, num_recommendations: int):
    """Log recommendation request for analytics"""
    try:
        logger.info(f"Request logged - Session: {session_id}, Time: {processing_time:.2f}s, Recs: {num_recommendations}")
        # Here you could add database logging, external analytics, etc.
    except Exception as e:
        logger.error(f"Failed to log request: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
