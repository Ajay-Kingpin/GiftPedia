"""
External Integration Manager
Coordinates all external integrations and provides a unified interface
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from .mcp_client import mcp_client, MCPServer
from .amazon_api import AmazonAPI, AmazonProduct
from .price_tracker import PriceTracker, ProductPrice
from .affiliate_manager import AffiliateManager, AffiliateLink
from .catalog_sync import CatalogSynchronizer, CatalogProduct

logger = logging.getLogger(__name__)

@dataclass
class IntegrationStatus:
    """Integration system status"""
    mcp_connected: bool
    amazon_connected: bool
    price_tracking_active: bool
    affiliate_links_active: bool
    catalog_sync_active: bool
    last_sync_time: datetime
    total_products: int
    active_affiliate_links: int
    total_revenue: float

@dataclass
class EnrichedProduct:
    """Enriched product with all integration data"""
    catalog_product: CatalogProduct
    price_info: Optional[ProductPrice]
    affiliate_link: Optional[AffiliateLink]
    confidence_score: float
    recommendation_reasons: List[str]

class IntegrationManager:
    """Main integration coordinator"""
    
    def __init__(self):
        self.mcp_client = mcp_client
        self.amazon_api = AmazonAPI()
        self.price_tracker = PriceTracker()
        self.affiliate_manager = AffiliateManager()
        self.catalog_sync = CatalogSynchronizer()
        
        # Integration status
        self.status = IntegrationStatus(
            mcp_connected=False,
            amazon_connected=False,
            price_tracking_active=False,
            affiliate_links_active=False,
            catalog_sync_active=False,
            last_sync_time=datetime.min,
            total_products=0,
            active_affiliate_links=0,
            total_revenue=0.0
        )
        
        # Configuration
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load integration configuration"""
        default_config = {
            "mcp_enabled": True,
            "amazon_enabled": True,
            "price_tracking_enabled": True,
            "affiliate_links_enabled": True,
            "catalog_sync_enabled": True,
            "auto_sync_interval_hours": 6,
            "price_update_interval_minutes": 30,
            "max_recommendations": 10,
            "min_confidence_score": 0.3,
            "price_drop_threshold": 10.0,
            "out_of_stock_filter": True
        }
        
        try:
            config_file = "data/integration_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            else:
                # Save default config
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        
        return default_config
    
    async def initialize(self) -> bool:
        """Initialize all integration systems"""
        try:
            logger.info("Initializing integration systems...")
            
            # Initialize MCP client
            if self.config["mcp_enabled"]:
                await self.mcp_client.initialize()
                self.status.mcp_connected = True
                logger.info("MCP client initialized")
            
            # Test Amazon API connection
            if self.config["amazon_enabled"]:
                # Test with a simple search
                test_products = self.amazon_api.search_products("test", 1)
                self.status.amazon_connected = len(test_products) > 0
                logger.info(f"Amazon API connection: {self.status.amazon_connected}")
            
            # Initialize price tracking
            if self.config["price_tracking_enabled"]:
                self.status.price_tracking_active = True
                logger.info("Price tracking initialized")
            
            # Initialize affiliate links
            if self.config["affiliate_links_enabled"]:
                self.status.affiliate_links_active = True
                logger.info("Affiliate links initialized")
            
            # Initialize catalog sync
            if self.config["catalog_sync_enabled"]:
                self.status.catalog_sync_active = True
                logger.info("Catalog sync initialized")
            
            # Update status
            await self.update_status()
            
            logger.info("Integration systems initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing integration systems: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup integration systems"""
        try:
            await self.mcp_client.close()
            await self.price_tracker.cleanup()
            logger.info("Integration systems cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def update_status(self):
        """Update integration status"""
        try:
            # Get catalog stats
            catalog_stats = self.catalog_sync.get_catalog_stats()
            self.status.total_products = catalog_stats["total_products"]
            
            # Get affiliate stats
            self.status.active_affiliate_links = len(self.affiliate_manager.links)
            
            # Calculate total revenue
            total_revenue = sum(link.revenue for link in self.affiliate_manager.links.values())
            self.status.total_revenue = total_revenue
            
            # Get last sync time
            if self.catalog_sync.last_sync_times:
                latest_sync = max(self.catalog_sync.last_sync_times.values())
                self.status.last_sync_time = latest_sync
            
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    async def search_products(self, query: str, category: str = None, limit: int = 20) -> List[EnrichedProduct]:
        """Search for products with full enrichment"""
        try:
            # Search catalog
            catalog_products = self.catalog_sync.search_catalog(query, category, limit)
            
            enriched_products = []
            
            for catalog_product in catalog_products:
                try:
                    # Get price information
                    price_info = None
                    if self.config["price_tracking_enabled"]:
                        price_info = await self.price_tracker.get_best_price(catalog_product.source_product_id)
                    
                    # Get affiliate link
                    affiliate_link = None
                    if self.config["affiliate_links_enabled"]:
                        link_id = f"{catalog_product.source}_{catalog_product.source_product_id}"
                        if link_id in self.affiliate_manager.links:
                            affiliate_link = self.affiliate_manager.links[link_id]
                    
                    # Calculate confidence score
                    confidence_score = self.calculate_confidence_score(catalog_product, price_info, query)
                    
                    # Generate recommendation reasons
                    reasons = self.generate_recommendation_reasons(catalog_product, price_info, query)
                    
                    # Create enriched product
                    enriched_product = EnrichedProduct(
                        catalog_product=catalog_product,
                        price_info=price_info,
                        affiliate_link=affiliate_link,
                        confidence_score=confidence_score,
                        recommendation_reasons=reasons
                    )
                    
                    # Apply filters
                    if self.should_include_product(enriched_product):
                        enriched_products.append(enriched_product)
                
                except Exception as e:
                    logger.error(f"Error enriching product {catalog_product.product_id}: {e}")
                    continue
            
            # Sort by confidence score
            enriched_products.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Limit results
            max_recommendations = self.config["max_recommendations"]
            return enriched_products[:max_recommendations]
            
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    def calculate_confidence_score(self, catalog_product: CatalogProduct, 
                                 price_info: Optional[ProductPrice], query: str) -> float:
        """Calculate confidence score for a product"""
        score = 0.0
        
        # Base score from catalog
        score += 0.3
        
        # Title match
        query_lower = query.lower()
        title_lower = catalog_product.title.lower()
        
        if query_lower in title_lower:
            score += 0.4
        else:
            # Partial word matches
            query_words = query_lower.split()
            title_words = title_lower.split()
            matches = sum(1 for word in query_words if word in title_words)
            score += (matches / len(query_words)) * 0.2
        
        # Tag matches
        if catalog_product.tags:
            tag_matches = sum(1 for tag in catalog_product.tags if query_lower in tag.lower())
            score += (tag_matches / len(catalog_product.tags)) * 0.1
        
        # Price information
        if price_info:
            score += 0.1
            
            # Price trend bonus
            if price_info.price_info.price_trend == "down":
                score += 0.05
            elif price_info.price_info.price_drop_percentage > self.config["price_drop_threshold"]:
                score += 0.1
        
        # Availability
        if catalog_product.availability.lower() == "in stock":
            score += 0.05
        elif catalog_product.availability.lower() == "out of stock":
            score -= 0.2
        
        # Affiliate link
        if catalog_product.affiliate_url:
            score += 0.05
        
        return min(max(score, 0.0), 1.0)
    
    def generate_recommendation_reasons(self, catalog_product: CatalogProduct, 
                                      price_info: Optional[ProductPrice], query: str) -> List[str]:
        """Generate recommendation reasons for a product"""
        reasons = []
        
        # Category match
        if catalog_product.category:
            reasons.append(f"Perfect {catalog_product.category.lower()} option")
        
        # Brand recognition
        if catalog_product.brand and catalog_product.brand.lower() != "generic":
            reasons.append(f"Trusted {catalog_product.brand} brand")
        
        # Price value
        if price_info:
            if price_info.price_info.price_trend == "down":
                reasons.append("Price has recently dropped")
            if price_info.price_info.price_drop_percentage > self.config["price_drop_threshold"]:
                reasons.append(f"Significant price drop: {price_info.price_info.price_drop_percentage:.1f}%")
        
        # Availability
        if catalog_product.availability.lower() == "in stock":
            reasons.append("Currently in stock and ready to ship")
        
        # Features
        if catalog_product.features:
            top_features = catalog_product.features[:2]
            for feature in top_features:
                if len(feature) < 50:  # Keep it concise
                    reasons.append(feature)
        
        # Quality indicators
        if catalog_product.brand.lower() in ["apple", "sony", "samsung", "lg", "microsoft"]:
            reasons.append("Premium quality brand")
        
        return reasons[:4]  # Limit to 4 reasons
    
    def should_include_product(self, enriched_product: EnrichedProduct) -> bool:
        """Check if product should be included in recommendations"""
        # Minimum confidence score
        if enriched_product.confidence_score < self.config["min_confidence_score"]:
            return False
        
        # Out of stock filter
        if (self.config["out_of_stock_filter"] and 
            enriched_product.catalog_product.availability.lower() == "out of stock"):
            return False
        
        # Minimum price (to avoid very cheap items)
        if enriched_product.catalog_product.price < 10:
            return False
        
        return True
    
    async def get_product_details(self, product_id: str) -> Optional[EnrichedProduct]:
        """Get detailed product information"""
        try:
            # Get from catalog
            catalog_product = self.catalog_sync.get_product_by_id(product_id)
            if not catalog_product:
                return None
            
            # Get price information
            price_info = None
            if self.config["price_tracking_enabled"]:
                price_info = await self.price_tracker.get_best_price(catalog_product.source_product_id)
            
            # Get affiliate link
            affiliate_link = None
            if self.config["affiliate_links_enabled"]:
                link_id = f"{catalog_product.source}_{catalog_product.source_product_id}"
                if link_id in self.affiliate_manager.links:
                    affiliate_link = self.affiliate_manager.links[link_id]
            
            # Calculate confidence score (default for details view)
            confidence_score = 0.8
            
            # Generate recommendation reasons
            reasons = self.generate_recommendation_reasons(catalog_product, price_info, "")
            
            return EnrichedProduct(
                catalog_product=catalog_product,
                price_info=price_info,
                affiliate_link=affiliate_link,
                confidence_score=confidence_score,
                recommendation_reasons=reasons
            )
            
        except Exception as e:
            logger.error(f"Error getting product details: {e}")
            return None
    
    async def sync_catalog(self) -> Dict[str, Any]:
        """Trigger catalog synchronization"""
        try:
            logger.info("Starting catalog synchronization...")
            sync_results = await self.catalog_sync.sync_all_sources()
            
            # Update status
            await self.update_status()
            
            logger.info("Catalog synchronization completed")
            return sync_results
            
        except Exception as e:
            logger.error(f"Error during catalog sync: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_price_alerts(self) -> List[Dict[str, Any]]:
        """Get price alerts for significant drops"""
        try:
            alerts = self.price_tracker.get_price_alerts(self.config["price_drop_threshold"])
            
            alert_data = []
            for price_data in alerts:
                catalog_product = self.catalog_sync.get_product_by_id(price_data.product_id)
                if catalog_product:
                    alert_data.append({
                        "product_id": price_data.product_id,
                        "title": catalog_product.title,
                        "brand": catalog_product.brand,
                        "current_price": price_data.price_info.current_price,
                        "currency": price_data.price_info.currency,
                        "price_drop_percentage": price_data.price_info.price_drop_percentage,
                        "price_trend": price_data.price_info.price_trend,
                        "affiliate_url": catalog_product.affiliate_url,
                        "image_url": catalog_product.image_url
                    })
            
            return alert_data
            
        except Exception as e:
            logger.error(f"Error getting price alerts: {e}")
            return []
    
    async def get_integration_status(self) -> IntegrationStatus:
        """Get current integration status"""
        await self.update_status()
        return self.status
    
    def get_revenue_report(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue report for the specified period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            total_revenue = 0.0
            total_conversions = 0
            total_clicks = 0
            
            network_performance = {}
            
            for network_name in self.affiliate_manager.networks:
                if self.affiliate_manager.networks[network_name].enabled:
                    perf = self.affiliate_manager.get_network_performance(network_name)
                    network_performance[network_name] = perf
                    total_revenue += perf["total_revenue"]
                    total_conversions += perf["total_conversions"]
                    total_clicks += perf["total_clicks"]
            
            return {
                "period_days": days,
                "total_revenue": total_revenue,
                "total_conversions": total_conversions,
                "total_clicks": total_clicks,
                "conversion_rate": (total_conversions / total_clicks * 100) if total_clicks > 0 else 0,
                "network_performance": network_performance,
                "top_performing_links": self.affiliate_manager.get_top_performing_links(10)
            }
            
        except Exception as e:
            logger.error(f"Error generating revenue report: {e}")
            return {"error": str(e)}

# Global integration manager instance
integration_manager = IntegrationManager()
