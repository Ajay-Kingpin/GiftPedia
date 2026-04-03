"""
Real-time Price and Availability Tracking System
Monitors product prices and availability across multiple sources
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .amazon_api import AmazonAPI, AmazonProduct

logger = logging.getLogger(__name__)

@dataclass
class PriceInfo:
    """Price information"""
    current_price: float
    currency: str
    availability: str
    last_updated: datetime
    price_history: List[Dict[str, Any]]
    price_trend: str  # 'up', 'down', 'stable'
    price_drop_percentage: float

@dataclass
class ProductPrice:
    """Product price tracking data"""
    product_id: str
    source: str  # 'amazon', 'flipkart', etc.
    title: str
    brand: str
    price_info: PriceInfo
    affiliate_url: str
    image_url: str
    category: str

class PriceTracker:
    """Real-time price and availability tracker"""
    
    def __init__(self):
        self.amazon_api = AmazonAPI()
        self.cache: Dict[str, ProductPrice] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
        
        # Rate limiting
        self.max_concurrent_requests = 5
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_requests)
        
        # Price tracking storage
        self.price_history_file = "data/price_history.json"
        self.load_price_history()
    
    def load_price_history(self):
        """Load price history from file"""
        try:
            if os.path.exists(self.price_history_file):
                with open(self.price_history_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Loaded price history for {len(data)} products")
            else:
                logger.info("No existing price history file found")
        except Exception as e:
            logger.error(f"Error loading price history: {e}")
    
    def save_price_history(self):
        """Save price history to file"""
        try:
            os.makedirs(os.path.dirname(self.price_history_file), exist_ok=True)
            with open(self.price_history_file, 'w') as f:
                json.dump({}, f)  # Simplified for now
            logger.info("Price history saved")
        except Exception as e:
            logger.error(f"Error saving price history: {e}")
    
    def _is_cache_valid(self, product_id: str) -> bool:
        """Check if cached data is still valid"""
        if product_id not in self.cache_expiry:
            return False
        return datetime.now() < self.cache_expiry[product_id]
    
    def _update_cache(self, product_id: str, product_price: ProductPrice):
        """Update cache with new data"""
        self.cache[product_id] = product_price
        self.cache_expiry[product_id] = datetime.now() + self.cache_duration
    
    def _calculate_price_trend(self, price_history: List[Dict[str, Any]]) -> str:
        """Calculate price trend based on history"""
        if len(price_history) < 2:
            return 'stable'
        
        recent_prices = price_history[:7]  # Last 7 data points
        if len(recent_prices) < 2:
            return 'stable'
        
        # Calculate average of first half vs second half
        mid_point = len(recent_prices) // 2
        first_half_avg = sum(p['price'] for p in recent_prices[:mid_point]) / mid_point
        second_half_avg = sum(p['price'] for p in recent_prices[mid_point:]) / (len(recent_prices) - mid_point)
        
        diff = second_half_avg - first_half_avg
        threshold = first_half_avg * 0.05  # 5% threshold
        
        if diff > threshold:
            return 'up'
        elif diff < -threshold:
            return 'down'
        else:
            return 'stable'
    
    def _calculate_price_drop(self, price_history: List[Dict[str, Any]], current_price: float) -> float:
        """Calculate price drop percentage from historical high"""
        if not price_history:
            return 0.0
        
        historical_high = max(p['price'] for p in price_history)
        if historical_high <= current_price:
            return 0.0
        
        drop_percentage = ((historical_high - current_price) / historical_high) * 100
        return round(drop_percentage, 2)
    
    async def get_amazon_price(self, asin: str) -> Optional[ProductPrice]:
        """Get price information from Amazon"""
        try:
            product = self.amazon_api.get_product_details(asin)
            if not product:
                return None
            
            # Get price history (mock implementation for now)
            price_history_data = self.amazon_api.get_price_history(asin, days=30)
            
            # Calculate trend and drop
            trend = self._calculate_price_trend(price_history_data)
            price_drop = self._calculate_price_drop(price_history_data, product.price)
            
            price_info = PriceInfo(
                current_price=product.price,
                currency=product.currency,
                availability=product.availability,
                last_updated=datetime.now(),
                price_history=price_history_data,
                price_trend=trend,
                price_drop_percentage=price_drop
            )
            
            product_price = ProductPrice(
                product_id=asin,
                source='amazon',
                title=product.title,
                brand=product.brand,
                price_info=price_info,
                affiliate_url=product.url,
                image_url=product.image_url,
                category=product.category
            )
            
            return product_price
            
        except Exception as e:
            logger.error(f"Error getting Amazon price for {asin}: {e}")
            return None
    
    async def get_flipkart_price(self, product_id: str) -> Optional[ProductPrice]:
        """Get price information from Flipkart (mock implementation)"""
        # Mock Flipkart integration
        try:
            # In a real implementation, this would call Flipkart's API
            mock_data = {
                'title': f'Product {product_id}',
                'brand': 'MockBrand',
                'price': 1299.99,
                'currency': 'INR',
                'availability': 'In Stock',
                'image_url': f'https://picsum.photos/seed/flipkart-{product_id}/400/300.jpg',
                'category': 'Electronics',
                'affiliate_url': f'https://www.flipkart.com/product/{product_id}'
            }
            
            price_history_data = [
                {
                    'date': (datetime.now() - timedelta(days=i)).isoformat(),
                    'price': mock_data['price'] + (hash(product_id + str(i)) % 100) - 50,
                    'currency': 'INR'
                }
                for i in range(30)
            ]
            
            trend = self._calculate_price_trend(price_history_data)
            price_drop = self._calculate_price_drop(price_history_data, mock_data['price'])
            
            price_info = PriceInfo(
                current_price=mock_data['price'],
                currency=mock_data['currency'],
                availability=mock_data['availability'],
                last_updated=datetime.now(),
                price_history=price_history_data,
                price_trend=trend,
                price_drop_percentage=price_drop
            )
            
            product_price = ProductPrice(
                product_id=product_id,
                source='flipkart',
                title=mock_data['title'],
                brand=mock_data['brand'],
                price_info=price_info,
                affiliate_url=mock_data['affiliate_url'],
                image_url=mock_data['image_url'],
                category=mock_data['category']
            )
            
            return product_price
            
        except Exception as e:
            logger.error(f"Error getting Flipkart price for {product_id}: {e}")
            return None
    
    async def track_product_prices(self, product_ids: List[str], sources: List[str] = None) -> Dict[str, ProductPrice]:
        """Track prices for multiple products across multiple sources"""
        if sources is None:
            sources = ['amazon', 'flipkart']
        
        results = {}
        tasks = []
        
        for product_id in product_ids:
            # Check cache first
            cache_key = f"{product_id}_amazon"
            if self._is_cache_valid(cache_key):
                results[cache_key] = self.cache[cache_key]
                continue
            
            # Add tasks for each source
            if 'amazon' in sources:
                tasks.append(('amazon', product_id, self.get_amazon_price(product_id)))
            
            if 'flipkart' in sources:
                tasks.append(('flipkart', product_id, self.get_flipkart_price(product_id)))
        
        # Execute tasks concurrently
        if tasks:
            loop = asyncio.get_event_loop()
            future_tasks = [loop.create_task(task[2]) for task in tasks]
            
            for i, future in enumerate(asyncio.as_completed(future_tasks)):
                try:
                    result = await future
                    if result:
                        source, product_id = tasks[i][0], tasks[i][1]
                        cache_key = f"{product_id}_{source}"
                        results[cache_key] = result
                        self._update_cache(cache_key, result)
                except Exception as e:
                    logger.error(f"Error in price tracking task: {e}")
        
        return results
    
    async def get_best_price(self, product_id: str) -> Optional[ProductPrice]:
        """Get the best price across all sources for a product"""
        prices = await self.track_product_prices([product_id])
        
        if not prices:
            return None
        
        # Find the lowest price
        best_price = None
        for price_data in prices.values():
            if best_price is None or price_data.price_info.current_price < best_price.price_info.current_price:
                best_price = price_data
        
        return best_price
    
    async def search_products_with_prices(self, query: str, max_results: int = 10) -> List[ProductPrice]:
        """Search for products and get their prices"""
        # Search Amazon
        amazon_products = self.amazon_api.search_products(query, max_results)
        
        # Get prices for found products
        asins = [product.asin for product in amazon_products]
        price_data = await self.track_product_prices(asins, ['amazon'])
        
        results = []
        for asin in asins:
            cache_key = f"{asin}_amazon"
            if cache_key in price_data:
                results.append(price_data[cache_key])
        
        logger.info(f"Found {len(results)} products with prices for query: {query}")
        return results
    
    def get_price_alerts(self, threshold_percentage: float = 20.0) -> List[ProductPrice]:
        """Get products with significant price drops"""
        alerts = []
        
        for product_price in self.cache.values():
            if product_price.price_info.price_drop_percentage >= threshold_percentage:
                alerts.append(product_price)
        
        return alerts
    
    async def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        self.save_price_history()

# Global price tracker instance
price_tracker = PriceTracker()
