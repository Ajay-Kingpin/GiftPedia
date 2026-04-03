"""
Product Catalog Synchronization System
Handles synchronization of product catalogs across multiple sources
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor

from .amazon_api import AmazonAPI, AmazonProduct
from .price_tracker import PriceTracker, ProductPrice
from .affiliate_manager import AffiliateManager, AffiliateLink

logger = logging.getLogger(__name__)

@dataclass
class CatalogProduct:
    """Unified product representation"""
    product_id: str
    source: str
    source_product_id: str
    title: str
    brand: str
    category: str
    subcategory: str
    price: float
    currency: str
    availability: str
    image_url: str
    description: str
    features: List[str]
    specifications: Dict[str, Any]
    tags: List[str]
    affiliate_url: str
    last_updated: datetime
    sync_status: str  # 'active', 'inactive', 'error'

@dataclass
class SyncConfig:
    """Synchronization configuration"""
    source_name: str
    enabled: bool
    sync_interval: timedelta
    batch_size: int
    max_products: int
    categories: List[str]
    price_threshold: float
    availability_required: bool

class CatalogSynchronizer:
    """Product catalog synchronization manager"""
    
    def __init__(self):
        self.catalog: Dict[str, CatalogProduct] = {}
        self.sync_configs: Dict[str, SyncConfig] = {}
        self.amazon_api = AmazonAPI()
        self.price_tracker = PriceTracker()
        self.affiliate_manager = AffiliateManager()
        
        # Catalog storage
        self.catalog_file = "data/product_catalog.json"
        self.sync_log_file = "data/sync_log.json"
        
        # Sync state
        self.last_sync_times: Dict[str, datetime] = {}
        self.sync_errors: Dict[str, List[str]] = {}
        
        # Setup default configurations
        self.setup_sync_configs()
        self.load_catalog()
    
    def setup_sync_configs(self):
        """Setup default synchronization configurations"""
        
        # Amazon sync config
        amazon_config = SyncConfig(
            source_name="amazon",
            enabled=True,
            sync_interval=timedelta(hours=6),  # Sync every 6 hours
            batch_size=50,
            max_products=1000,
            categories=["electronics", "books", "clothing", "home", "sports", "toys"],
            price_threshold=10.0,
            availability_required=True
        )
        
        # Flipkart sync config
        flipkart_config = SyncConfig(
            source_name="flipkart",
            enabled=True,
            sync_interval=timedelta(hours=12),  # Sync every 12 hours
            batch_size=30,
            max_products=500,
            categories=["electronics", "fashion", "home", "sports"],
            price_threshold=5.0,
            availability_required=True
        )
        
        self.sync_configs["amazon"] = amazon_config
        self.sync_configs["flipkart"] = flipkart_config
    
    def load_catalog(self):
        """Load existing catalog from file"""
        try:
            if os.path.exists(self.catalog_file):
                with open(self.catalog_file, 'r') as f:
                    data = json.load(f)
                    for product_id, product_data in data.items():
                        product_data['last_updated'] = datetime.fromisoformat(product_data['last_updated'])
                        self.catalog[product_id] = CatalogProduct(**product_data)
                    logger.info(f"Loaded {len(self.catalog)} products from catalog")
            else:
                logger.info("No existing catalog file found")
        except Exception as e:
            logger.error(f"Error loading catalog: {e}")
    
    def save_catalog(self):
        """Save catalog to file"""
        try:
            os.makedirs(os.path.dirname(self.catalog_file), exist_ok=True)
            
            # Convert to serializable format
            serializable_catalog = {}
            for product_id, product in self.catalog.items():
                product_dict = asdict(product)
                product_dict['last_updated'] = product.last_updated.isoformat()
                serializable_catalog[product_id] = product_dict
            
            with open(self.catalog_file, 'w') as f:
                json.dump(serializable_catalog, f, indent=2)
            
            logger.info(f"Saved {len(self.catalog)} products to catalog")
        except Exception as e:
            logger.error(f"Error saving catalog: {e}")
    
    def generate_product_id(self, source: str, source_product_id: str, title: str) -> str:
        """Generate unique product ID"""
        content = f"{source}_{source_product_id}_{title}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def normalize_category(self, category: str) -> str:
        """Normalize category name"""
        category_mapping = {
            "electronics": "Electronics",
            "electronic": "Electronics",
            "computers": "Electronics",
            "phones": "Electronics",
            "books": "Books",
            "book": "Books",
            "clothing": "Fashion",
            "fashion": "Fashion",
            "apparel": "Fashion",
            "home": "Home & Kitchen",
            "kitchen": "Home & Kitchen",
            "sports": "Sports & Outdoors",
            "fitness": "Sports & Outdoors",
            "toys": "Toys & Games",
            "games": "Toys & Games"
        }
        
        normalized = category.lower()
        return category_mapping.get(normalized, category.title())
    
    async def sync_amazon_products(self, config: SyncConfig) -> Dict[str, Any]:
        """Synchronize products from Amazon"""
        if not config.enabled:
            return {"status": "skipped", "reason": "disabled"}
        
        sync_result = {
            "source": "amazon",
            "status": "running",
            "products_added": 0,
            "products_updated": 0,
            "products_removed": 0,
            "errors": []
        }
        
        try:
            # Search for products in each category
            all_products = []
            
            for category in config.categories:
                try:
                    # Search with multiple keywords for each category
                    category_keywords = self.get_category_keywords(category)
                    
                    for keyword in category_keywords:
                        products = self.amazon_api.search_products(keyword, config.batch_size)
                        all_products.extend(products)
                        
                        # Limit total products
                        if len(all_products) >= config.max_products:
                            break
                    
                    if len(all_products) >= config.max_products:
                        break
                        
                except Exception as e:
                    error_msg = f"Error searching Amazon for category {category}: {e}"
                    sync_result["errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Process found products
            for amazon_product in all_products[:config.max_products]:
                try:
                    # Apply filters
                    if amazon_product.price < config.price_threshold:
                        continue
                    
                    if config.availability_required and "Available" not in amazon_product.availability:
                        continue
                    
                    # Generate unified product ID
                    product_id = self.generate_product_id("amazon", amazon_product.asin, amazon_product.title)
                    
                    # Create affiliate link
                    affiliate_link = self.affiliate_manager.create_affiliate_link(
                        product_id=amazon_product.asin,
                        source="amazon",
                        original_url=amazon_product.url,
                        category=amazon_product.category.lower()
                    )
                    
                    # Create catalog product
                    catalog_product = CatalogProduct(
                        product_id=product_id,
                        source="amazon",
                        source_product_id=amazon_product.asin,
                        title=amazon_product.title,
                        brand=amazon_product.brand,
                        category=self.normalize_category(amazon_product.category),
                        subcategory=amazon_product.category,
                        price=amazon_product.price,
                        currency=amazon_product.currency,
                        availability=amazon_product.availability,
                        image_url=amazon_product.image_url,
                        description="",  # Would need additional API call
                        features=amazon_product.features,
                        specifications={},  # Would need additional API call
                        tags=self.extract_tags(amazon_product.title, amazon_product.features),
                        affiliate_url=affiliate_link.affiliate_url,
                        last_updated=datetime.now(),
                        sync_status="active"
                    )
                    
                    # Add or update catalog
                    if product_id in self.catalog:
                        # Update existing product
                        existing = self.catalog[product_id]
                        if catalog_product.last_updated > existing.last_updated:
                            self.catalog[product_id] = catalog_product
                            sync_result["products_updated"] += 1
                    else:
                        # Add new product
                        self.catalog[product_id] = catalog_product
                        sync_result["products_added"] += 1
                
                except Exception as e:
                    error_msg = f"Error processing Amazon product {amazon_product.asin}: {e}"
                    sync_result["errors"].append(error_msg)
                    logger.error(error_msg)
            
            sync_result["status"] = "completed"
            logger.info(f"Amazon sync completed: {sync_result['products_added']} added, {sync_result['products_updated']} updated")
            
        except Exception as e:
            sync_result["status"] = "failed"
            sync_result["errors"].append(f"Amazon sync failed: {e}")
            logger.error(f"Amazon sync failed: {e}")
        
        return sync_result
    
    async def sync_flipkart_products(self, config: SyncConfig) -> Dict[str, Any]:
        """Synchronize products from Flipkart (mock implementation)"""
        if not config.enabled:
            return {"status": "skipped", "reason": "disabled"}
        
        sync_result = {
            "source": "flipkart",
            "status": "running",
            "products_added": 0,
            "products_updated": 0,
            "products_removed": 0,
            "errors": []
        }
        
        try:
            # Mock Flipkart products (in real implementation, this would call Flipkart API)
            mock_products = [
                {
                    "source_product_id": f"FLIP{i:04d}",
                    "title": f"Flipkart Product {i}",
                    "brand": f"Brand{i}",
                    "category": config.categories[i % len(config.categories)],
                    "price": 1000 + (i * 100),
                    "currency": "INR",
                    "availability": "In Stock",
                    "image_url": f"https://picsum.photos/seed/flipkart{i}/400/300.jpg",
                    "description": f"Description for Flipkart product {i}",
                    "features": [f"Feature {j}" for j in range(3)]
                }
                for i in range(min(config.max_products, 100))  # Limit to 100 for mock
            ]
            
            for mock_product in mock_products:
                try:
                    # Apply filters
                    if mock_product["price"] < config.price_threshold:
                        continue
                    
                    # Generate unified product ID
                    product_id = self.generate_product_id("flipkart", mock_product["source_product_id"], mock_product["title"])
                    
                    # Create affiliate link
                    affiliate_link = self.affiliate_manager.create_affiliate_link(
                        product_id=mock_product["source_product_id"],
                        source="flipkart",
                        original_url=f"https://www.flipkart.com/product/{mock_product['source_product_id']}",
                        category=mock_product["category"].lower()
                    )
                    
                    # Create catalog product
                    catalog_product = CatalogProduct(
                        product_id=product_id,
                        source="flipkart",
                        source_product_id=mock_product["source_product_id"],
                        title=mock_product["title"],
                        brand=mock_product["brand"],
                        category=self.normalize_category(mock_product["category"]),
                        subcategory=mock_product["category"],
                        price=mock_product["price"],
                        currency=mock_product["currency"],
                        availability=mock_product["availability"],
                        image_url=mock_product["image_url"],
                        description=mock_product["description"],
                        features=mock_product["features"],
                        specifications={},
                        tags=self.extract_tags(mock_product["title"], mock_product["features"]),
                        affiliate_url=affiliate_link.affiliate_url,
                        last_updated=datetime.now(),
                        sync_status="active"
                    )
                    
                    # Add or update catalog
                    if product_id in self.catalog:
                        existing = self.catalog[product_id]
                        if catalog_product.last_updated > existing.last_updated:
                            self.catalog[product_id] = catalog_product
                            sync_result["products_updated"] += 1
                    else:
                        self.catalog[product_id] = catalog_product
                        sync_result["products_added"] += 1
                
                except Exception as e:
                    error_msg = f"Error processing Flipkart product {mock_product['source_product_id']}: {e}"
                    sync_result["errors"].append(error_msg)
                    logger.error(error_msg)
            
            sync_result["status"] = "completed"
            logger.info(f"Flipkart sync completed: {sync_result['products_added']} added, {sync_result['products_updated']} updated")
            
        except Exception as e:
            sync_result["status"] = "failed"
            sync_result["errors"].append(f"Flipkart sync failed: {e}")
            logger.error(f"Flipkart sync failed: {e}")
        
        return sync_result
    
    def get_category_keywords(self, category: str) -> List[str]:
        """Get search keywords for a category"""
        category_keywords = {
            "electronics": ["electronics", "gadgets", "smartphone", "laptop", "headphones", "camera"],
            "books": ["books", "novels", "textbooks", "audiobooks", "ebooks"],
            "clothing": ["clothing", "fashion", "shirts", "pants", "dresses", "shoes"],
            "home": ["home", "kitchen", "furniture", "decor", "appliances"],
            "sports": ["sports", "fitness", "exercise", "outdoor", "equipment"],
            "toys": ["toys", "games", "puzzles", "lego", "board games"]
        }
        
        return category_keywords.get(category.lower(), [category])
    
    def extract_tags(self, title: str, features: List[str]) -> List[str]:
        """Extract tags from title and features"""
        tags = []
        
        # Extract from title
        title_words = title.lower().split()
        common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        for word in title_words:
            if len(word) > 3 and word not in common_words:
                tags.append(word)
        
        # Extract from features
        for feature in features:
            feature_words = feature.lower().split()
            for word in feature_words:
                if len(word) > 3 and word not in common_words and word not in tags:
                    tags.append(word)
        
        # Limit tags
        return tags[:10]
    
    async def sync_all_sources(self) -> Dict[str, Any]:
        """Synchronize all enabled sources"""
        sync_results = {}
        
        # Sync each source
        for source_name, config in self.sync_configs.items():
            try:
                # Check if sync is needed
                last_sync = self.last_sync_times.get(source_name, datetime.min)
                if datetime.now() - last_sync < config.sync_interval:
                    sync_results[source_name] = {
                        "status": "skipped",
                        "reason": "too_soon",
                        "next_sync": (last_sync + config.sync_interval).isoformat()
                    }
                    continue
                
                logger.info(f"Starting sync for {source_name}")
                
                if source_name == "amazon":
                    sync_results[source_name] = await self.sync_amazon_products(config)
                elif source_name == "flipkart":
                    sync_results[source_name] = await self.sync_flipkart_products(config)
                
                # Update last sync time
                self.last_sync_times[source_name] = datetime.now()
                
            except Exception as e:
                sync_results[source_name] = {
                    "status": "failed",
                    "errors": [str(e)]
                }
                logger.error(f"Sync failed for {source_name}: {e}")
        
        # Save catalog after sync
        self.save_catalog()
        
        return sync_results
    
    def search_catalog(self, query: str, category: str = None, limit: int = 20) -> List[CatalogProduct]:
        """Search the unified catalog"""
        query_lower = query.lower()
        results = []
        
        for product in self.catalog.values():
            if product.sync_status != "active":
                continue
            
            # Category filter
            if category and product.category.lower() != category.lower():
                continue
            
            # Search in title, description, tags
            searchable_text = f"{product.title} {product.description} {' '.join(product.tags)}".lower()
            
            if query_lower in searchable_text:
                results.append(product)
        
        # Sort by relevance (simple implementation - by title match first)
        results.sort(key=lambda x: query_lower in x.title.lower(), reverse=True)
        
        return results[:limit]
    
    def get_product_by_id(self, product_id: str) -> Optional[CatalogProduct]:
        """Get product by ID"""
        return self.catalog.get(product_id)
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        stats = {
            "total_products": len(self.catalog),
            "by_source": {},
            "by_category": {},
            "by_sync_status": {},
            "last_updated": None
        }
        
        for product in self.catalog.values():
            # By source
            source = product.source
            stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
            
            # By category
            category = product.category
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # By sync status
            status = product.sync_status
            stats["by_sync_status"][status] = stats["by_sync_status"].get(status, 0) + 1
            
            # Last updated
            if stats["last_updated"] is None or product.last_updated > stats["last_updated"]:
                stats["last_updated"] = product.last_updated
        
        return stats
    
    async def cleanup_inactive_products(self, days: int = 30):
        """Remove inactive products from catalog"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        inactive_products = [
            product_id for product_id, product in self.catalog.items()
            if product.sync_status == "inactive" or product.last_updated < cutoff_time
        ]
        
        for product_id in inactive_products:
            del self.catalog[product_id]
        
        self.save_catalog()
        logger.info(f"Cleaned up {len(inactive_products)} inactive products")

# Global catalog synchronizer instance
catalog_sync = CatalogSynchronizer()
