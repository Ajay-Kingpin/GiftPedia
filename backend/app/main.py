from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="GiftPedia API",
    description="AI-powered gift recommendation system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://gift-pedia.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
API_KEY = os.getenv("API_KEY", "dev-api-key")

# Rate limiting (simple in-memory store)
rate_limit_store = {}

class RecommendationRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class UserProfile(BaseModel):
    recipient_age: Optional[int]
    recipient_gender: str
    interests: list[str]
    relationship: str
    occasion: str
    budget_inr: Optional[int]
    constraints: list[str]

class Product(BaseModel):
    product_id: str
    name: str
    category: str
    subcategory: str
    price_inr: float
    brand: Optional[str]
    image_url: str
    affiliate_link: str
    confidence_score: Optional[int]
    explanation: Optional[str]

class RecommendationResponse(BaseModel):
    recommendations: list[Product]
    profile: UserProfile
    processing_time: float
    session_id: str

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials

def rate_limit_check(client_ip: str):
    current_time = time.time()
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Remove old requests (older than 24 hours)
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip] 
        if current_time - req_time < 86400
    ]
    
    # Check if under 500 requests per day
    if len(rate_limit_store[client_ip]) >= 500:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limit_store[client_ip].append(current_time)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/api/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_api_key),
    client_ip: str = "localhost"  # In real app, get from request
):
    # Rate limiting check
    rate_limit_check(client_ip)
    
    start_time = time.time()
    
    try:
        # TODO: Implement orchestration logic
        # For now, return mock response
        mock_profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar", "audio"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
        )
        
        mock_products = [
            Product(
                product_id="mock_1",
                name="Fender Custom Guitar Strap",
                category="Music & Instruments",
                subcategory="Guitar Straps",
                price_inr=1899.0,
                brand="Fender",
                image_url="https://example.com/image.jpg",
                affiliate_link="https://amazon.in/dp/B08N5WRWSN",
                confidence_score=5,
                explanation="Perfect for musicians who want comfort and style"
            )
        ]
        
        processing_time = time.time() - start_time
        
        return RecommendationResponse(
            recommendations=mock_products,
            profile=mock_profile,
            processing_time=processing_time,
            session_id=request.session_id or f"session_{int(time.time())}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
