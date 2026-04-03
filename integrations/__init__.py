"""
External Integrations Package
Handles all external API integrations and data sources
"""

from .mcp_client import mcp_client, MCPClient, MCPServer, MCPResource
from .amazon_api import amazon_api, AmazonAPI, AmazonProduct
from .price_tracker import price_tracker, PriceTracker, ProductPrice, PriceInfo
from .affiliate_manager import affiliate_manager, AffiliateManager, AffiliateLink, AffiliateNetwork
from .catalog_sync import catalog_sync, CatalogSynchronizer, CatalogProduct, SyncConfig
from .integration_manager import integration_manager, IntegrationManager, IntegrationStatus, EnrichedProduct

__all__ = [
    # MCP Client
    'mcp_client',
    'MCPClient',
    'MCPServer',
    'MCPResource',
    
    # Amazon API
    'amazon_api',
    'AmazonAPI',
    'AmazonProduct',
    
    # Price Tracker
    'price_tracker',
    'PriceTracker',
    'ProductPrice',
    'PriceInfo',
    
    # Affiliate Manager
    'affiliate_manager',
    'AffiliateManager',
    'AffiliateLink',
    'AffiliateNetwork',
    
    # Catalog Sync
    'catalog_sync',
    'CatalogSynchronizer',
    'CatalogProduct',
    'SyncConfig',
    
    # Integration Manager
    'integration_manager',
    'IntegrationManager',
    'IntegrationStatus',
    'EnrichedProduct'
]

# Package initialization
import logging
logger = logging.getLogger(__name__)

async def initialize_integrations():
    """Initialize all integration systems"""
    try:
        logger.info("Initializing external integrations...")
        
        # Initialize the main integration manager
        success = await integration_manager.initialize()
        
        if success:
            logger.info("External integrations initialized successfully")
        else:
            logger.error("Failed to initialize external integrations")
        
        return success
        
    except Exception as e:
        logger.error(f"Error initializing integrations: {e}")
        return False

async def cleanup_integrations():
    """Cleanup all integration systems"""
    try:
        logger.info("Cleaning up external integrations...")
        await integration_manager.cleanup()
        logger.info("External integrations cleaned up")
    except Exception as e:
        logger.error(f"Error cleaning up integrations: {e}")
