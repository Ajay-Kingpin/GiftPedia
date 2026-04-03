"""
Amazon Product Advertising API Integration
Handles product searches, price checking, and affiliate link generation
"""

import os
import json
import logging
import hashlib
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from urllib.parse import urlencode, quote
import base64
import hmac

logger = logging.getLogger(__name__)

@dataclass
class AmazonProduct:
    """Amazon product representation"""
    asin: str
    title: str
    brand: str
    price: float
    currency: str
    availability: str
    url: str
    image_url: str
    category: str
    features: List[str]
    rating: Optional[float] = None
    review_count: Optional[int] = None
    affiliate_url: Optional[str] = None

class AmazonAPI:
    """Amazon Product Advertising API client"""
    
    def __init__(self):
        self.access_key = os.getenv("AMAZON_ACCESS_KEY")
        self.secret_key = os.getenv("AMAZON_SECRET_KEY")
        self.associate_tag = os.getenv("AMAZON_ASSOCIATE_TAG")
        self.marketplace = os.getenv("AMAZON_MARKETPLACE", "www.amazon.com")
        self.region = os.getenv("AMAZON_REGION", "us-east-1")
        
        # API endpoints
        self.base_url = f"https://{self.marketplace}/paapi5"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 1 second between requests
        
        if not all([self.access_key, self.secret_key, self.associate_tag]):
            logger.warning("Amazon API credentials not fully configured")
    
    def _sign_request(self, method: str, uri: str, params: Dict[str, str]) -> Dict[str, str]:
        """Sign Amazon API request"""
        # Create canonical request
        canonical_query = urlencode(sorted(params.items()))
        canonical_headers = f"host:{self.marketplace}\n"
        signed_headers = "host"
        payload_hash = hashlib.sha256(''.encode('utf-8')).hexdigest()
        
        canonical_request = f"{method}\n{uri}\n{canonical_query}\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
        
        # Create string to sign
        algorithm = "AWS4-HMAC-SHA256"
        date_stamp = datetime.utcnow().strftime('%Y%m%d')
        credential_scope = f"{date_stamp}/{self.region}/paapi5/aws4_request"
        string_to_sign = f"{algorithm}\n{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        
        # Calculate signature
        k_date = hmac.new(f"AWS4{self.secret_key}".encode('utf-8'), date_stamp.encode('utf-8'), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode('utf-8'), hashlib.sha256).digest()
        k_service = hmac.new(k_region, "paapi5".encode('utf-8'), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, "aws4_request".encode('utf-8'), hashlib.sha256).digest()
        
        signature = hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
        
        # Add signature to parameters
        params['Signature'] = signature
        
        return params
    
    def _make_request(self, endpoint: str, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Amazon API"""
        if not all([self.access_key, self.secret_key, self.associate_tag]):
            logger.error("Amazon API credentials not configured")
            return None
        
        # Rate limiting
        current_time = time.time()
        if current_time - self.last_request_time < self.min_request_interval:
            time.sleep(self.min_request_interval - (current_time - self.last_request_time))
        
        try:
            # Add required parameters
            params.update({
                'AWSAccessKeyId': self.access_key,
                'AssociateTag': self.associate_tag,
                'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'Version': 'v1'
            })
            
            # Sign the request
            signed_params = self._sign_request('GET', f'/paapi5{endpoint}', params)
            
            # Make the request
            url = f"{self.base_url}{endpoint}?{urlencode(signed_params)}"
            response = requests.get(url, timeout=30)
            
            self.last_request_time = time.time()
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Amazon API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error making Amazon API request: {e}")
            return None
    
    def search_products(self, keywords: str, item_count: int = 10) -> List[AmazonProduct]:
        """Search for products on Amazon"""
        params = {
            'Keywords': keywords,
            'ItemCount': str(item_count),
            'Resources': 'Images.Primary.Medium,ItemInfo.Title,ItemInfo.Features,ItemInfo.ProductInfo,ItemInfo.ByLineInfo,Offers.Listings.Price,Offers.Listings.Availability,Offers.Listings.DeliveryInfo,BrowseNodeInfo.BrowseNodes'
        }
        
        response = self._make_request('/searchitems', params)
        
        if not response:
            return []
        
        products = []
        
        for item in response.get('SearchResult', {}).get('Items', []):
            try:
                # Extract product information
                asin = item.get('ASIN')
                title = item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', '')
                
                # Brand information
                brand = item.get('ItemInfo', {}).get('ByLineInfo', {}).get('Brand', {}).get('DisplayValue', '')
                
                # Price information
                price = 0.0
                currency = 'USD'
                listings = item.get('Offers', {}).get('Listings', [])
                if listings:
                    price = listings[0].get('Price', {}).get('DisplayAmount', '0').replace('$', '').replace(',', '')
                    try:
                        price = float(price)
                    except ValueError:
                        price = 0.0
                    currency = listings[0].get('Price', {}).get('Currency', 'USD')
                
                # Availability
                availability = 'Unknown'
                if listings:
                    availability = listings[0].get('Availability', {}).get('Message', 'Unknown')
                
                # Image URL
                image_url = item.get('Images', {}).get('Primary', {}).get('Medium', {}).get('URL', '')
                
                # Category
                category = 'General'
                browse_nodes = item.get('BrowseNodeInfo', {}).get('BrowseNodes', [])
                if browse_nodes:
                    category = browse_nodes[0].get('DisplayName', 'General')
                
                # Features
                features = []
                features_data = item.get('ItemInfo', {}).get('Features', {}).get('DisplayValues', [])
                if features_data:
                    features = features_data[:5]  # Limit to first 5 features
                
                # Rating and reviews
                rating = None
                review_count = None
                reviews_data = item.get('CustomerReviews', {})
                if reviews_data:
                    rating = reviews_data.get('StarRating', {}).get('DisplayValue')
                    review_count = reviews_data.get('Count', {}).get('DisplayValue')
                    try:
                        rating = float(rating) if rating else None
                        review_count = int(review_count) if review_count else None
                    except (ValueError, TypeError):
                        rating = None
                        review_count = None
                
                # Detail page URL
                detail_page_url = item.get('DetailPageURL', '')
                
                product = AmazonProduct(
                    asin=asin,
                    title=title,
                    brand=brand,
                    price=price,
                    currency=currency,
                    availability=availability,
                    url=detail_page_url,
                    image_url=image_url,
                    category=category,
                    features=features,
                    rating=rating,
                    review_count=review_count
                )
                
                products.append(product)
                
            except Exception as e:
                logger.error(f"Error parsing Amazon product: {e}")
                continue
        
        logger.info(f"Found {len(products)} Amazon products for keywords: {keywords}")
        return products
    
    def get_product_details(self, asin: str) -> Optional[AmazonProduct]:
        """Get detailed information for a specific product"""
        params = {
            'ASIN': asin,
            'Resources': 'Images.Primary.Medium,ItemInfo.Title,ItemInfo.Features,ItemInfo.ProductInfo,ItemInfo.ByLineInfo,Offers.Listings.Price,Offers.Listings.Availability,Offers.Listings.DeliveryInfo,BrowseNodeInfo.BrowseNodes,CustomerReviews'
        }
        
        response = self._make_request('/getitems', params)
        
        if not response:
            return None
        
        items = response.get('ItemsResult', {}).get('Items', [])
        if not items:
            return None
        
        item = items[0]
        
        try:
            # Extract product information (similar to search_products)
            title = item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', '')
            brand = item.get('ItemInfo', {}).get('ByLineInfo', {}).get('Brand', {}).get('DisplayValue', '')
            
            # Price information
            price = 0.0
            currency = 'USD'
            listings = item.get('Offers', {}).get('Listings', [])
            if listings:
                price_str = listings[0].get('Price', {}).get('DisplayAmount', '0').replace('$', '').replace(',', '')
                try:
                    price = float(price_str)
                except ValueError:
                    price = 0.0
                currency = listings[0].get('Price', {}).get('Currency', 'USD')
            
            # Availability
            availability = listings[0].get('Availability', {}).get('Message', 'Unknown') if listings else 'Unknown'
            
            # Image URL
            image_url = item.get('Images', {}).get('Primary', {}).get('Medium', {}).get('URL', '')
            
            # Category
            category = 'General'
            browse_nodes = item.get('BrowseNodeInfo', {}).get('BrowseNodes', [])
            if browse_nodes:
                category = browse_nodes[0].get('DisplayName', 'General')
            
            # Features
            features = []
            features_data = item.get('ItemInfo', {}).get('Features', {}).get('DisplayValues', [])
            if features_data:
                features = features_data[:5]
            
            # Rating and reviews
            rating = None
            review_count = None
            reviews_data = item.get('CustomerReviews', {})
            if reviews_data:
                rating_str = reviews_data.get('StarRating', {}).get('DisplayValue')
                review_count_str = reviews_data.get('Count', {}).get('DisplayValue')
                try:
                    rating = float(rating_str) if rating_str else None
                    review_count = int(review_count_str) if review_count_str else None
                except (ValueError, TypeError):
                    rating = None
                    review_count = None
            
            # Detail page URL
            detail_page_url = item.get('DetailPageURL', '')
            
            product = AmazonProduct(
                asin=asin,
                title=title,
                brand=brand,
                price=price,
                currency=currency,
                availability=availability,
                url=detail_page_url,
                image_url=image_url,
                category=category,
                features=features,
                rating=rating,
                review_count=review_count
            )
            
            return product
            
        except Exception as e:
            logger.error(f"Error parsing Amazon product details: {e}")
            return None
    
    def generate_affiliate_url(self, asin: str) -> str:
        """Generate affiliate URL for a product"""
        base_url = f"https://{self.marketplace}/dp/{asin}"
        return f"{base_url}?tag={self.associate_tag}"
    
    def get_price_history(self, asin: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get price history for a product (mock implementation)"""
        # This would typically call a price tracking service
        # For now, return mock data
        mock_history = []
        base_price = 100.0 + (hash(asin) % 200)  # Base price based on ASIN
        
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            # Add some random variation
            price_variation = (hash(asin + str(i)) % 20) - 10
            price = base_price + price_variation
            
            mock_history.append({
                'date': date.isoformat(),
                'price': max(0, price),
                'currency': 'USD'
            })
        
        return mock_history

# Global Amazon API instance
amazon_api = AmazonAPI()
