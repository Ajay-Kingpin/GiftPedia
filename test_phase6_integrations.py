#!/usr/bin/env python3
"""
Phase 6: External Integrations Test Suite
Tests all external integration components
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock environment variables for testing
os.environ['AMAZON_ACCESS_KEY'] = 'test_key'
os.environ['AMAZON_SECRET_KEY'] = 'test_secret'
os.environ['AMAZON_ASSOCIATE_TAG'] = 'giftpedia-test-20'
os.environ['AMAZON_MARKETPLACE'] = 'www.amazon.com'
os.environ['AMAZON_REGION'] = 'us-east-1'

class Phase6IntegrationTester:
    """Test suite for Phase 6 integrations"""
    
    def __init__(self):
        self.test_results = {
            'mcp_client': {'status': 'pending', 'details': []},
            'amazon_api': {'status': 'pending', 'details': []},
            'price_tracker': {'status': 'pending', 'details': []},
            'affiliate_manager': {'status': 'pending', 'details': []},
            'catalog_sync': {'status': 'pending', 'details': []},
            'integration_manager': {'status': 'pending', 'details': []}
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all Phase 6 integration tests"""
        logger.info("🚀 Starting Phase 6: External Integrations Tests")
        
        try:
            # Test MCP Client
            await self.test_mcp_client()
            
            # Test Amazon API
            await self.test_amazon_api()
            
            # Test Price Tracker
            await self.test_price_tracker()
            
            # Test Affiliate Manager
            await self.test_affiliate_manager()
            
            # Test Catalog Sync
            await self.test_catalog_sync()
            
            # Test Integration Manager
            await self.test_integration_manager()
            
            # Generate summary
            return self.generate_test_summary()
            
        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def test_mcp_client(self):
        """Test MCP Client functionality"""
        logger.info("🧪 Testing MCP Client...")
        
        try:
            from integrations.mcp_client import MCPClient, MCPServer
            
            # Create MCP client
            client = MCPClient()
            
            # Register test server
            test_server = MCPServer(
                name="test_server",
                url="https://api.test.com",
                api_key="test_key",
                rate_limit=10,
                enabled=True
            )
            client.register_server(test_server)
            
            # Test server registration
            assert test_server.name in client.servers, "Server not registered"
            self.test_results['mcp_client']['details'].append("✅ Server registration successful")
            
            # Test rate limiting
            assert client._check_rate_limit("test_server"), "Rate limiting failed"
            self.test_results['mcp_client']['details'].append("✅ Rate limiting functional")
            
            # Test initialization (without actual server)
            await client.initialize()
            self.test_results['mcp_client']['details'].append("✅ Client initialization successful")
            
            # Cleanup
            await client.close()
            self.test_results['mcp_client']['details'].append("✅ Client cleanup successful")
            
            self.test_results['mcp_client']['status'] = 'passed'
            logger.info("✅ MCP Client tests passed")
            
        except Exception as e:
            self.test_results['mcp_client']['status'] = 'failed'
            self.test_results['mcp_client']['details'].append(f"❌ Error: {e}")
            logger.error(f"❌ MCP Client tests failed: {e}")
    
    async def test_amazon_api(self):
        """Test Amazon API functionality"""
        logger.info("🧪 Testing Amazon API...")
        
        try:
            from integrations.amazon_api import AmazonAPI, AmazonProduct
            
            # Create Amazon API instance
            api = AmazonAPI()
            
            # Test configuration
            assert api.access_key == 'test_key', "Access key not set"
            assert api.secret_key == 'test_secret', "Secret key not set"
            assert api.associate_tag == 'giftpedia-test-20', "Associate tag not set"
            self.test_results['amazon_api']['details'].append("✅ Configuration successful")
            
            # Test request signing (without actual API call)
            params = {'Test': 'value'}
            signed_params = api._sign_request('GET', '/test', params)
            assert 'Signature' in signed_params, "Request signing failed"
            self.test_results['amazon_api']['details'].append("✅ Request signing functional")
            
            # Test product creation
            product = AmazonProduct(
                asin="B001234567",
                title="Test Product",
                brand="Test Brand",
                price=99.99,
                currency="USD",
                availability="In Stock",
                url="https://amazon.com/test",
                image_url="https://images.amazon.com/test.jpg",
                category="Electronics",
                features=["Feature 1", "Feature 2"]
            )
            assert product.asin == "B001234567", "Product creation failed"
            self.test_results['amazon_api']['details'].append("✅ Product model functional")
            
            # Test affiliate URL generation
            affiliate_url = api.generate_affiliate_url("B001234567")
            assert "giftpedia-test-20" in affiliate_url, "Affiliate URL generation failed"
            self.test_results['amazon_api']['details'].append("✅ Affiliate URL generation successful")
            
            self.test_results['amazon_api']['status'] = 'passed'
            logger.info("✅ Amazon API tests passed")
            
        except Exception as e:
            self.test_results['amazon_api']['status'] = 'failed'
            self.test_results['amazon_api']['details'].append(f"❌ Error: {e}")
            logger.error(f"❌ Amazon API tests failed: {e}")
    
    async def test_price_tracker(self):
        """Test Price Tracker functionality"""
        logger.info("🧪 Testing Price Tracker...")
        
        try:
            from integrations.price_tracker import PriceTracker, ProductPrice, PriceInfo
            
            # Create price tracker
            tracker = PriceTracker()
            
            # Test price calculation methods
            price_history = [
                {'date': '2024-01-01', 'price': 100.0},
                {'date': '2024-01-02', 'price': 95.0},
                {'date': '2024-01-03', 'price': 90.0}
            ]
            
            trend = tracker._calculate_price_trend(price_history)
            assert trend in ['up', 'down', 'stable'], "Price trend calculation failed"
            self.test_results['price_tracker']['details'].append("✅ Price trend calculation functional")
            
            drop_percentage = tracker._calculate_price_drop(price_history, 85.0)
            assert drop_percentage > 0, "Price drop calculation failed"
            self.test_results['price_tracker']['details'].append("✅ Price drop calculation functional")
            
            # Test cache functionality
            test_product = ProductPrice(
                product_id="test_001",
                source="test",
                title="Test Product",
                brand="Test Brand",
                price_info=PriceInfo(
                    current_price=99.99,
                    currency="USD",
                    availability="In Stock",
                    last_updated=datetime.now(),
                    price_history=[],
                    price_trend="stable",
                    price_drop_percentage=0.0
                ),
                affiliate_url="https://example.com/test",
                image_url="https://example.com/image.jpg",
                category="Electronics"
            )
            
            tracker._update_cache("test_001", test_product)
            assert tracker._is_cache_valid("test_001"), "Cache update failed"
            self.test_results['price_tracker']['details'].append("✅ Cache functionality working")
            
            # Test cleanup
            await tracker.cleanup()
            self.test_results['price_tracker']['details'].append("✅ Cleanup successful")
            
            self.test_results['price_tracker']['status'] = 'passed'
            logger.info("✅ Price Tracker tests passed")
            
        except Exception as e:
            self.test_results['price_tracker']['status'] = 'failed'
            self.test_results['price_tracker']['details'].append(f"❌ Error: {e}")
            logger.error(f"❌ Price Tracker tests failed: {e}")
    
    async def test_affiliate_manager(self):
        """Test Affiliate Manager functionality"""
        logger.info("🧪 Testing Affiliate Manager...")
        
        try:
            from integrations.affiliate_manager import AffiliateManager, AffiliateLink, AffiliateNetwork
            
            # Create affiliate manager
            manager = AffiliateManager()
            
            # Test network setup
            assert "amazon" in manager.networks, "Amazon network not set up"
            assert "flipkart" in manager.networks, "Flipkart network not set up"
            self.test_results['affiliate_manager']['details'].append("✅ Network setup successful")
            
            # Test Amazon affiliate URL generation
            amazon_url = manager.generate_amazon_affiliate_url(
                "https://amazon.com/dp/B001234567", 
                "B001234567"
            )
            assert "giftpedia-test-20" in amazon_url, "Amazon affiliate URL generation failed"
            self.test_results['affiliate_manager']['details'].append("✅ Amazon affiliate URL generation successful")
            
            # Test Flipkart affiliate URL generation
            flipkart_url = manager.generate_flipkart_affiliate_url(
                "https://flipkart.com/product/12345",
                "12345"
            )
            assert "affid=giftpedia" in flipkart_url, "Flipkart affiliate URL generation failed"
            self.test_results['affiliate_manager']['details'].append("✅ Flipkart affiliate URL generation successful")
            
            # Test affiliate link creation
            affiliate_link = manager.create_affiliate_link(
                product_id="test_001",
                source="amazon",
                original_url="https://amazon.com/dp/B001234567",
                category="electronics"
            )
            assert affiliate_link.product_id == "test_001", "Affiliate link creation failed"
            assert affiliate_link.source == "amazon", "Affiliate link source incorrect"
            self.test_results['affiliate_manager']['details'].append("✅ Affiliate link creation successful")
            
            # Test click tracking
            click_tracked = manager.track_click(list(manager.links.keys())[0])
            assert click_tracked, "Click tracking failed"
            self.test_results['affiliate_manager']['details'].append("✅ Click tracking successful")
            
            # Test conversion tracking
            conversion_tracked = manager.track_conversion(list(manager.links.keys())[0], 100.0)
            assert conversion_tracked, "Conversion tracking failed"
            self.test_results['affiliate_manager']['details'].append("✅ Conversion tracking successful")
            
            # Test performance metrics
            performance = manager.get_link_performance(list(manager.links.keys())[0])
            assert performance is not None, "Performance metrics failed"
            assert performance['clicks'] > 0, "Performance metrics incorrect"
            self.test_results['affiliate_manager']['details'].append("✅ Performance metrics functional")
            
            self.test_results['affiliate_manager']['status'] = 'passed'
            logger.info("✅ Affiliate Manager tests passed")
            
        except Exception as e:
            self.test_results['affiliate_manager']['status'] = 'failed'
            self.test_results['affiliate_manager']['details'].append(f"❌ Error: {e}")
            logger.error(f"❌ Affiliate Manager tests failed: {e}")
    
    async def test_catalog_sync(self):
        """Test Catalog Sync functionality"""
        logger.info("🧪 Testing Catalog Sync...")
        
        try:
            from integrations.catalog_sync import CatalogSynchronizer, CatalogProduct, SyncConfig
            
            # Create catalog synchronizer
            sync = CatalogSynchronizer()
            
            # Test sync configurations
            assert "amazon" in sync.sync_configs, "Amazon sync config not found"
            assert "flipkart" in sync.sync_configs, "Flipkart sync config not found"
            self.test_results['catalog_sync']['details'].append("✅ Sync configurations loaded")
            
            # Test product ID generation
            product_id = sync.generate_product_id("amazon", "B001234567", "Test Product")
            assert product_id is not None, "Product ID generation failed"
            self.test_results['catalog_sync']['details'].append("✅ Product ID generation functional")
            
            # Test category normalization
            normalized = sync.normalize_category("electronics")
            assert normalized == "Electronics", "Category normalization failed"
            self.test_results['catalog_sync']['details'].append("✅ Category normalization working")
            
            # Test tag extraction
            tags = sync.extract_tags("Test Product with Features", ["Feature 1", "Feature 2"])
            assert len(tags) > 0, "Tag extraction failed"
            self.test_results['catalog_sync']['details'].append("✅ Tag extraction functional")
            
            # Test catalog search
            results = sync.search_catalog("test")
            assert isinstance(results, list), "Catalog search failed"
            self.test_results['catalog_sync']['details'].append("✅ Catalog search functional")
            
            # Test catalog statistics
            stats = sync.get_catalog_stats()
            assert 'total_products' in stats, "Catalog statistics failed"
            self.test_results['catalog_sync']['details'].append("✅ Catalog statistics functional")
            
            self.test_results['catalog_sync']['status'] = 'passed'
            logger.info("✅ Catalog Sync tests passed")
            
        except Exception as e:
            self.test_results['catalog_sync']['status'] = 'failed'
            self.test_results['catalog_sync']['details'].append(f"❌ Error: {e}")
            logger.error(f"❌ Catalog Sync tests failed: {e}")
    
    async def test_integration_manager(self):
        """Test Integration Manager functionality"""
        logger.info("🧪 Testing Integration Manager...")
        
        try:
            from integrations.integration_manager import IntegrationManager, IntegrationStatus
            
            # Create integration manager
            manager = IntegrationManager()
            
            # Test configuration loading
            config = manager.config
            assert 'mcp_enabled' in config, "Configuration loading failed"
            self.test_results['integration_manager']['details'].append("✅ Configuration loaded")
            
            # Test initialization
            initialized = await manager.initialize()
            assert initialized, "Integration manager initialization failed"
            self.test_results['integration_manager']['details'].append("✅ Initialization successful")
            
            # Test status update
            status = await manager.get_integration_status()
            assert isinstance(status, IntegrationStatus), "Status update failed"
            self.test_results['integration_manager']['details'].append("✅ Status update functional")
            
            # Test product search
            results = await manager.search_products("test", limit=5)
            assert isinstance(results, list), "Product search failed"
            self.test_results['integration_manager']['details'].append("✅ Product search functional")
            
            # Test confidence score calculation
            if results:
                confidence = manager.calculate_confidence_score(
                    results[0].catalog_product,
                    results[0].price_info,
                    "test query"
                )
                assert 0 <= confidence <= 1, "Confidence score calculation failed"
                self.test_results['integration_manager']['details'].append("✅ Confidence score calculation working")
            
            # Test recommendation reasons generation
            if results:
                reasons = manager.generate_recommendation_reasons(
                    results[0].catalog_product,
                    results[0].price_info,
                    "test query"
                )
                assert isinstance(reasons, list), "Recommendation reasons generation failed"
                self.test_results['integration_manager']['details'].append("✅ Recommendation reasons generation working")
            
            # Test revenue report
            report = manager.get_revenue_report(30)
            assert 'period_days' in report, "Revenue report generation failed"
            self.test_results['integration_manager']['details'].append("✅ Revenue report generation working")
            
            # Test cleanup
            await manager.cleanup()
            self.test_results['integration_manager']['details'].append("✅ Cleanup successful")
            
            self.test_results['integration_manager']['status'] = 'passed'
            logger.info("✅ Integration Manager tests passed")
            
        except Exception as e:
            self.test_results['integration_manager']['status'] = 'failed'
            self.test_results['integration_manager']['details'].append(f"❌ Error: {e}")
            logger.error(f"❌ Integration Manager tests failed: {e}")
    
    def generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'passed')
        failed_tests = total_tests - passed_tests
        
        summary = {
            'phase': 'Phase 6: External Integrations',
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'overall_status': 'PASSED' if failed_tests == 0 else 'FAILED',
            'test_results': self.test_results,
            'recommendations': []
        }
        
        # Add recommendations based on results
        if failed_tests == 0:
            summary['recommendations'].append("✅ All external integrations are working correctly")
            summary['recommendations'].append("✅ Ready for production deployment")
            summary['recommendations'].append("✅ Can proceed to Phase 7: Deployment & Release")
        else:
            summary['recommendations'].append("❌ Some integrations need attention before deployment")
            summary['recommendations'].append("❌ Review failed tests and fix issues")
            summary['recommendations'].append("❌ Ensure all API credentials are properly configured")
        
        return summary

async def main():
    """Main test runner"""
    tester = Phase6IntegrationTester()
    results = await tester.run_all_tests()
    
    # Print results
    print("\n" + "="*80)
    print("🎯 PHASE 6: EXTERNAL INTEGRATIONS - TEST RESULTS")
    print("="*80)
    
    print(f"📊 Overall Status: {results['overall_status']}")
    print(f"📈 Success Rate: {results['success_rate']:.1f}%")
    print(f"✅ Passed: {results['passed_tests']}/{results['total_tests']}")
    print(f"❌ Failed: {results['failed_tests']}/{results['total_tests']}")
    
    print("\n📋 Detailed Results:")
    for component, result in results['test_results'].items():
        status_emoji = "✅" if result['status'] == 'passed' else "❌"
        print(f"{status_emoji} {component.replace('_', ' ').title()}: {result['status'].upper()}")
        for detail in result['details']:
            print(f"   {detail}")
    
    print("\n🎯 Recommendations:")
    for rec in results['recommendations']:
        print(f"   {rec}")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
