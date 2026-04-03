"""
Affiliate Link Generation and Management System
Handles affiliate link generation, tracking, and revenue management
"""

import os
import json
import logging
import hashlib
import urllib.parse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import requests
from urllib.parse import urlencode, quote

logger = logging.getLogger(__name__)

@dataclass
class AffiliateLink:
    """Affiliate link representation"""
    product_id: str
    source: str
    original_url: str
    affiliate_url: str
    tracking_id: str
    commission_rate: float
    created_at: datetime
    clicks: int
    conversions: int
    revenue: float

@dataclass
class AffiliateNetwork:
    """Affiliate network configuration"""
    name: str
    tracking_id: str
    api_key: Optional[str]
    commission_rates: Dict[str, float]  # category -> rate
    base_url: str
    enabled: bool

class AffiliateManager:
    """Affiliate link generation and management"""
    
    def __init__(self):
        self.networks: Dict[str, AffiliateNetwork] = {}
        self.links: Dict[str, AffiliateLink] = {}
        self.click_tracking: Dict[str, List[datetime]] = {}
        
        # Load configuration
        self.setup_networks()
        self.load_tracking_data()
    
    def setup_networks(self):
        """Setup affiliate networks"""
        
        # Amazon Associates
        amazon_network = AffiliateNetwork(
            name="amazon",
            tracking_id=os.getenv("AMAZON_ASSOCIATE_TAG", "giftpedia-20"),
            api_key=None,
            commission_rates={
                "electronics": 4.0,
                "books": 4.5,
                "clothing": 7.0,
                "home": 5.5,
                "sports": 6.0,
                "toys": 6.5,
                "default": 4.0
            },
            base_url="https://www.amazon.com",
            enabled=True
        )
        
        # Flipkart Affiliate
        flipkart_network = AffiliateNetwork(
            name="flipkart",
            tracking_id=os.getenv("FLIPKART_AFFILIATE_ID", "giftpedia"),
            api_key=os.getenv("FLIPKART_API_KEY"),
            commission_rates={
                "electronics": 6.0,
                "fashion": 10.0,
                "home": 8.0,
                "sports": 7.5,
                "default": 6.0
            },
            base_url="https://www.flipkart.com",
            enabled=True
        )
        
        # Commission Junction (CJ)
        cj_network = AffiliateNetwork(
            name="commission_junction",
            tracking_id=os.getenv("CJ_AFFILIATE_ID", "giftpedia"),
            api_key=os.getenv("CJ_API_KEY"),
            commission_rates={
                "technology": 3.5,
                "fashion": 8.0,
                "home": 5.5,
                "sports": 6.0,
                "default": 4.0
            },
            base_url="https://www.anrdoezrs.net",
            enabled=False  # Requires API setup
        )
        
        self.networks["amazon"] = amazon_network
        self.networks["flipkart"] = flipkart_network
        self.networks["commission_junction"] = cj_network
    
    def load_tracking_data(self):
        """Load tracking data from file"""
        try:
            tracking_file = "data/affiliate_tracking.json"
            if os.path.exists(tracking_file):
                with open(tracking_file, 'r') as f:
                    data = json.load(f)
                    # Convert data back to AffiliateLink objects
                    for link_id, link_data in data.items():
                        link_data['created_at'] = datetime.fromisoformat(link_data['created_at'])
                        self.links[link_id] = AffiliateLink(**link_data)
                    logger.info(f"Loaded {len(self.links)} affiliate links")
        except Exception as e:
            logger.error(f"Error loading tracking data: {e}")
    
    def save_tracking_data(self):
        """Save tracking data to file"""
        try:
            os.makedirs("data", exist_ok=True)
            tracking_file = "data/affiliate_tracking.json"
            
            # Convert to serializable format
            serializable_data = {}
            for link_id, link in self.links.items():
                link_dict = asdict(link)
                link_dict['created_at'] = link.created_at.isoformat()
                serializable_data[link_id] = link_dict
            
            with open(tracking_file, 'w') as f:
                json.dump(serializable_data, f, indent=2)
            
            logger.info("Affiliate tracking data saved")
        except Exception as e:
            logger.error(f"Error saving tracking data: {e}")
    
    def generate_amazon_affiliate_url(self, product_url: str, asin: str) -> str:
        """Generate Amazon affiliate URL"""
        network = self.networks["amazon"]
        if not network.enabled:
            return product_url
        
        # Extract ASIN if not provided
        if not asin:
            # Extract ASIN from URL
            if "/dp/" in product_url:
                asin = product_url.split("/dp/")[1].split("/")[0]
            elif "/gp/product/" in product_url:
                asin = product_url.split("/gp/product/")[1].split("/")[0]
        
        # Generate affiliate URL
        if asin:
            affiliate_url = f"{network.base_url}/dp/{asin}?tag={network.tracking_id}"
        else:
            # Fallback: add tracking parameter to original URL
            separator = "&" if "?" in product_url else "?"
            affiliate_url = f"{product_url}{separator}tag={network.tracking_id}"
        
        return affiliate_url
    
    def generate_flipkart_affiliate_url(self, product_url: str, product_id: str) -> str:
        """Generate Flipkart affiliate URL"""
        network = self.networks["flipkart"]
        if not network.enabled:
            return product_url
        
        # Generate affiliate URL
        if product_id:
            affiliate_url = f"{network.base_url}/{product_id}?affid={network.tracking_id}"
        else:
            # Fallback: add tracking parameter
            separator = "&" if "?" in product_url else "?"
            affiliate_url = f"{product_url}{separator}affid={network.tracking_id}"
        
        return affiliate_url
    
    def generate_cj_affiliate_url(self, product_url: str, advertiser_id: str) -> str:
        """Generate Commission Junction affiliate URL"""
        network = self.networks["commission_junction"]
        if not network.enabled:
            return product_url
        
        # Generate CJ affiliate URL
        affiliate_url = f"{network.base_url}/click-{network.tracking_id}-{advertiser_id}"
        
        return affiliate_url
    
    def create_affiliate_link(self, product_id: str, source: str, original_url: str, 
                            category: str = "default", additional_params: Dict[str, str] = None) -> AffiliateLink:
        """Create an affiliate link"""
        
        # Generate link ID
        link_id = hashlib.md5(f"{product_id}_{source}_{original_url}".encode()).hexdigest()
        
        # Check if link already exists
        if link_id in self.links:
            return self.links[link_id]
        
        # Generate affiliate URL based on source
        affiliate_url = original_url
        commission_rate = 0.0
        
        if source == "amazon":
            affiliate_url = self.generate_amazon_affiliate_url(original_url, product_id)
            commission_rate = self.networks["amazon"].commission_rates.get(category.lower(), 4.0)
        elif source == "flipkart":
            affiliate_url = self.generate_flipkart_affiliate_url(original_url, product_id)
            commission_rate = self.networks["flipkart"].commission_rates.get(category.lower(), 6.0)
        elif source == "commission_junction":
            affiliate_url = self.generate_cj_affiliate_url(original_url, additional_params.get("advertiser_id", ""))
            commission_rate = self.networks["commission_junction"].commission_rates.get(category.lower(), 4.0)
        
        # Create affiliate link object
        affiliate_link = AffiliateLink(
            product_id=product_id,
            source=source,
            original_url=original_url,
            affiliate_url=affiliate_url,
            tracking_id=self.networks[source].tracking_id,
            commission_rate=commission_rate,
            created_at=datetime.now(),
            clicks=0,
            conversions=0,
            revenue=0.0
        )
        
        # Store link
        self.links[link_id] = affiliate_link
        self.click_tracking[link_id] = []
        
        # Save tracking data
        self.save_tracking_data()
        
        logger.info(f"Created affiliate link for {product_id} from {source}")
        return affiliate_link
    
    def track_click(self, link_id: str, user_agent: str = None, ip_address: str = None) -> bool:
        """Track a click on an affiliate link"""
        if link_id not in self.links:
            return False
        
        # Record click
        self.links[link_id].clicks += 1
        self.click_tracking[link_id].append(datetime.now())
        
        # Save tracking data
        self.save_tracking_data()
        
        logger.info(f"Tracked click for link {link_id}")
        return True
    
    def track_conversion(self, link_id: str, amount: float) -> bool:
        """Track a conversion (sale)"""
        if link_id not in self.links:
            return False
        
        # Calculate revenue
        revenue = amount * (self.links[link_id].commission_rate / 100)
        
        # Update conversion data
        self.links[link_id].conversions += 1
        self.links[link_id].revenue += revenue
        
        # Save tracking data
        self.save_tracking_data()
        
        logger.info(f"Tracked conversion for link {link_id}: ₹{amount:.2f} (Revenue: ₹{revenue:.2f})")
        return True
    
    def get_link_performance(self, link_id: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for an affiliate link"""
        if link_id not in self.links:
            return None
        
        link = self.links[link_id]
        clicks = link.clicks
        conversions = link.conversions
        revenue = link.revenue
        
        # Calculate metrics
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
        avg_revenue_per_click = revenue / clicks if clicks > 0 else 0
        avg_revenue_per_conversion = revenue / conversions if conversions > 0 else 0
        
        return {
            "link_id": link_id,
            "product_id": link.product_id,
            "source": link.source,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "conversion_rate": conversion_rate,
            "avg_revenue_per_click": avg_revenue_per_click,
            "avg_revenue_per_conversion": avg_revenue_per_conversion,
            "commission_rate": link.commission_rate
        }
    
    def get_network_performance(self, network_name: str) -> Dict[str, Any]:
        """Get performance metrics for an entire network"""
        network_links = [link for link in self.links.values() if link.source == network_name]
        
        total_clicks = sum(link.clicks for link in network_links)
        total_conversions = sum(link.conversions for link in network_links)
        total_revenue = sum(link.revenue for link in network_links)
        
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        
        return {
            "network": network_name,
            "total_links": len(network_links),
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_revenue": total_revenue,
            "conversion_rate": conversion_rate,
            "enabled": self.networks[network_name].enabled
        }
    
    def get_top_performing_links(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing affiliate links"""
        performances = []
        
        for link_id in self.links:
            perf = self.get_link_performance(link_id)
            if perf and perf["clicks"] > 0:
                performances.append(perf)
        
        # Sort by revenue
        performances.sort(key=lambda x: x["revenue"], reverse=True)
        
        return performances[:limit]
    
    def get_recent_clicks(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent clicks for monitoring"""
        recent_clicks = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for link_id, click_times in self.click_tracking.items():
            for click_time in click_times:
                if click_time > cutoff_time:
                    link = self.links[link_id]
                    recent_clicks.append({
                        "link_id": link_id,
                        "product_id": link.product_id,
                        "source": link.source,
                        "click_time": click_time.isoformat(),
                        "affiliate_url": link.affiliate_url
                    })
        
        # Sort by click time (most recent first)
        recent_clicks.sort(key=lambda x: x["click_time"], reverse=True)
        
        return recent_clicks
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old tracking data"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Clean up click tracking
        for link_id in list(self.click_tracking.keys()):
            self.click_tracking[link_id] = [
                click_time for click_time in self.click_tracking[link_id] 
                if click_time > cutoff_time
            ]
            
            # Remove empty click tracking
            if not self.click_tracking[link_id]:
                del self.click_tracking[link_id]
        
        logger.info(f"Cleaned up tracking data older than {days} days")

# Global affiliate manager instance
affiliate_manager = AffiliateManager()
