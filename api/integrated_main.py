"""
GiftPedia API with Phase 6 External Integrations
Real Amazon API, Price Tracking, Affiliate Links, and Catalog Sync
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add integrations to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import Phase 6 integrations
from integrations.integration_manager import integration_manager, EnrichedProduct
from integrations.amazon_api import AmazonAPI
from integrations.price_tracker import PriceTracker
from integrations.affiliate_manager import AffiliateManager
from integrations.catalog_sync import CatalogSynchronizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys from environment
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
AMAZON_ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY')
AMAZON_SECRET_KEY = os.getenv('AMAZON_SECRET_KEY')
AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG')
AMAZON_MARKETPLACE = os.getenv('AMAZON_MARKETPLACE', 'www.amazon.in')
AMAZON_REGION = os.getenv('AMAZON_REGION', 'ap-south-1')

# Pydantic models
class RecommendationRequest(BaseModel):
    user_input: str = Field(..., description="User's gift request description")
    session_id: Optional[str] = None

class RecommendationResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None
    session_id: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None

class ProductResponse(BaseModel):
    product_id: str
    name: str
    brand: str
    price: float
    currency: str
    availability: str
    image_url: str
    category: str
    features: List[str]
    affiliate_url: Optional[str]
    confidence_score: float
    recommendation_reasons: List[str]
    price_info: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    service: str
    integrations: Dict[str, Any]

# Global integration manager
integration_manager_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup integrations"""
    global integration_manager_instance
    
    logger.info("Starting GiftPedia API with Phase 6 Integrations...")
    
    # Initialize Phase 6 integrations with real API keys
    try:
        success = await integration_manager.initialize(
            gemini_api_key=GEMINI_API_KEY,
            amazon_access_key=AMAZON_ACCESS_KEY,
            amazon_secret_key=AMAZON_SECRET_KEY,
            amazon_associate_tag=AMAZON_ASSOCIATE_TAG,
            amazon_marketplace=AMAZON_MARKETPLACE,
            amazon_region=AMAZON_REGION
        )
        if success:
            integration_manager_instance = integration_manager
            logger.info("Phase 6 integrations initialized successfully with real API keys")
        else:
            logger.error("Failed to initialize Phase 6 integrations")
    except Exception as e:
        logger.error(f"Error initializing integrations: {e}")
    
    yield
    
    # Cleanup
    try:
        await integration_manager.cleanup()
        logger.info("Phase 6 integrations cleaned up")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Create FastAPI app
app = FastAPI(
    title="GiftPedia API - Phase 6 Integrated",
    description="GiftPedia API with real external integrations",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "http://localhost:3002",
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IntegratedGiftService:
    """Gift recommendation service with Phase 6 integrations"""
    
    def __init__(self):
        self.amazon_api = AmazonAPI()
        self.price_tracker = PriceTracker()
        self.affiliate_manager = AffiliateManager()
        self.catalog_sync = CatalogSynchronizer()
    
    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """Get gift recommendations using Phase 6 integrations"""
        start_time = datetime.now()
        session_id = request.session_id or f"session_{int(start_time.timestamp())}"
        
        try:
            # Extract key information from user input
            keywords = self._extract_keywords(request.user_input)
            
            # Search for products using Phase 6 integrations
            enriched_products = await integration_manager.search_products(
                query=keywords,
                limit=5
            )
            
            # Convert to response format
            recommendations = []
            for enriched_product in enriched_products:
                product_data = ProductResponse(
                    product_id=enriched_product.catalog_product.product_id,
                    name=enriched_product.catalog_product.title,
                    brand=enriched_product.catalog_product.brand,
                    price=enriched_product.catalog_product.price,
                    currency=enriched_product.catalog_product.currency,
                    availability=enriched_product.catalog_product.availability,
                    image_url=enriched_product.catalog_product.image_url,
                    category=enriched_product.catalog_product.category,
                    features=enriched_product.catalog_product.features,
                    affiliate_url=enriched_product.catalog_product.affiliate_url,
                    confidence_score=enriched_product.confidence_score,
                    recommendation_reasons=enriched_product.recommendation_reasons,
                    price_info={
                        "current_price": enriched_product.price_info.current_price if enriched_product.price_info else None,
                        "price_trend": enriched_product.price_info.price_trend if enriched_product.price_info else None,
                        "price_drop_percentage": enriched_product.price_info.price_drop_percentage if enriched_product.price_info else None,
                        "last_updated": enriched_product.price_info.last_updated.isoformat() if enriched_product.price_info else None
                    } if enriched_product.price_info else None
                )
                recommendations.append(product_data.dict())
            
            # Create response
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return RecommendationResponse(
                success=True,
                data={
                    "recommendations": recommendations,
                    "query": keywords,
                    "total_results": len(recommendations)
                },
                processing_time=processing_time,
                session_id=session_id,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return RecommendationResponse(
                success=False,
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds(),
                session_id=session_id,
                timestamp=datetime.now().isoformat()
            )
    
    def _extract_keywords(self, user_input: str) -> str:
        """Extract keywords from user input"""
        # Simple keyword extraction - in production, this would use NLP
        words = user_input.lower().split()
        # Filter out common words
        stop_words = {'the', 'for', 'who', 'loves', 'likes', 'enjoys', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'from', 'with', 'by'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return ' '.join(keywords[:5])  # Limit to 5 keywords

# Initialize service
app.state.recommendation_service = IntegratedGiftService()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check with Phase 6 integration status"""
    try:
        integration_status = await integration_manager.get_integration_status()
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="2.0.0",
            service="GiftPedia API - Phase 6 Integrated",
            integrations={
                "mcp_connected": integration_status.mcp_connected,
                "amazon_connected": integration_status.amazon_connected,
                "price_tracking_active": integration_status.price_tracking_active,
                "affiliate_links_active": integration_status.affiliate_links_active,
                "catalog_sync_active": integration_status.catalog_sync_active,
                "total_products": integration_status.total_products,
                "active_affiliate_links": integration_status.active_affiliate_links,
                "total_revenue": integration_status.total_revenue,
                "last_sync_time": integration_status.last_sync_time.isoformat() if integration_status.last_sync_time else None
            }
        )
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="2.0.0",
            service="GiftPedia API - Phase 6 Integrated",
            integrations={"error": str(e)}
        )

@app.post("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """Get gift recommendations using Phase 6 integrations"""
    service = app.state.recommendation_service
    return await service.get_recommendations(request)

@app.get("/categories", response_model=List[Dict[str, Any]])
async def get_categories():
    """Get available product categories from catalog sync"""
    try:
        stats = await integration_manager.catalog_sync.get_catalog_stats()
        categories = []
        
        for category, count in stats.get("by_category", {}).items():
            categories.append({
                "name": category,
                "product_count": count,
                "description": f"Products in {category}"
            })
        
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return []

@app.get("/products/{product_id}", response_model=Dict[str, Any])
async def get_product_details(product_id: str):
    """Get detailed product information using Phase 6 integrations"""
    try:
        enriched_product = await integration_manager.get_product_details(product_id)
        if not enriched_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "product_id": enriched_product.catalog_product.product_id,
            "name": enriched_product.catalog_product.title,
            "brand": enriched_product.catalog_product.brand,
            "price": enriched_product.catalog_product.price,
            "currency": enriched_product.catalog_product.currency,
            "availability": enriched_product.catalog_product.availability,
            "image_url": enriched_product.catalog_product.image_url,
            "category": enriched_product.catalog_product.category,
            "subcategory": enriched_product.catalog_product.subcategory,
            "description": enriched_product.catalog_product.description,
            "features": enriched_product.catalog_product.features,
            "specifications": enriched_product.catalog_product.specifications,
            "tags": enriched_product.catalog_product.tags,
            "affiliate_url": enriched_product.catalog_product.affiliate_url,
            "confidence_score": enriched_product.confidence_score,
            "recommendation_reasons": enriched_product.recommendation_reasons,
            "price_info": {
                "current_price": enriched_product.price_info.current_price if enriched_product.price_info else None,
                "currency": enriched_product.price_info.currency if enriched_product.price_info else None,
                "availability": enriched_product.price_info.availability if enriched_product.price_info else None,
                "price_trend": enriched_product.price_info.price_trend if enriched_product.price_info else None,
                "price_drop_percentage": enriched_product.price_info.price_drop_percentage if enriched_product.price_info else None,
                "last_updated": enriched_product.price_info.last_updated.isoformat() if enriched_product.price_info else None,
                "price_history": enriched_product.price_info.price_history if enriched_product.price_info else []
            } if enriched_product.price_info else None,
            "affiliate_info": {
                "source": enriched_product.affiliate_link.source if enriched_product.affiliate_link else None,
                "tracking_id": enriched_product.affiliate_link.tracking_id if enriched_product.affiliate_link else None,
                "commission_rate": enriched_product.affiliate_link.commission_rate if enriched_product.affiliate_link else None,
                "clicks": enriched_product.affiliate_link.clicks if enriched_product.affiliate_link else 0,
                "conversions": enriched_product.affiliate_link.conversions if enriched_product.affiliate_link else 0,
                "revenue": enriched_product.affiliate_link.revenue if enriched_product.affiliate_link else 0.0
            } if enriched_product.affiliate_link else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/popular-gifts", response_model=List[Dict[str, Any]])
async def get_popular_gifts(category: Optional[str] = None, limit: int = 10):
    """Get popular gifts from catalog sync"""
    try:
        # Search catalog for popular products
        products = await integration_manager.search_products(
            query=category or "popular",
            limit=limit
        )
        
        result = []
        for product in products:
            result.append({
                "product_id": product.catalog_product.product_id,
                "name": product.catalog_product.title,
                "brand": product.catalog_product.brand,
                "price": product.catalog_product.price,
                "currency": product.catalog_product.currency,
                "image_url": product.catalog_product.image_url,
                "category": product.catalog_product.category,
                "availability": product.catalog_product.availability,
                "confidence_score": product.confidence_score,
                "price_trend": product.price_info.price_trend if product.price_info else "stable",
                "price_drop": product.price_info.price_drop_percentage if product.price_info else 0.0
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting popular gifts: {e}")
        return []

@app.get("/price-alerts", response_model=List[Dict[str, Any]])
async def get_price_alerts():
    """Get price alerts for significant drops"""
    try:
        alerts = await integration_manager.get_price_alerts(10.0)  # 10% threshold
        return alerts
    except Exception as e:
        logger.error(f"Error getting price alerts: {e}")
        return []

@app.post("/sync-catalog", response_model=Dict[str, Any])
async def sync_catalog():
    """Trigger catalog synchronization"""
    try:
        results = await integration_manager.sync_catalog()
        return results
    except Exception as e:
        logger.error(f"Error syncing catalog: {e}")
        return {"status": "failed", "error": str(e)}

@app.get("/revenue-report", response_model=Dict[str, Any])
async def get_revenue_report(days: int = 30):
    """Get revenue report for the specified period"""
    try:
        report = integration_manager.get_revenue_report(days)
        return report
    except Exception as e:
        logger.error(f"Error getting revenue report: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
