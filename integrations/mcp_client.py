"""
MCP (Model Context Protocol) Client for External Integrations
Handles connections to external MCP servers for enhanced data sources
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class MCPServer:
    """MCP Server configuration"""
    name: str
    url: str
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    enabled: bool = True

@dataclass
class MCPResource:
    """MCP Resource representation"""
    uri: str
    name: str
    description: str
    mime_type: str
    metadata: Dict[str, Any]

class MCPClient:
    """MCP Client for external integrations"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServer] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits: Dict[str, List[datetime]] = {}
        
    def register_server(self, server: MCPServer):
        """Register an MCP server"""
        self.servers[server.name] = server
        self.rate_limits[server.name] = []
        logger.info(f"Registered MCP server: {server.name}")
    
    async def initialize(self):
        """Initialize the MCP client"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"User-Agent": "GiftPedia-MCP-Client/1.0"}
        )
        logger.info("MCP Client initialized")
    
    async def close(self):
        """Close the MCP client"""
        if self.session:
            await self.session.close()
        logger.info("MCP Client closed")
    
    def _check_rate_limit(self, server_name: str) -> bool:
        """Check if we're within rate limits"""
        if server_name not in self.rate_limits:
            return True
        
        server = self.servers[server_name]
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Remove old requests
        self.rate_limits[server_name] = [
            req_time for req_time in self.rate_limits[server_name] 
            if req_time > cutoff
        ]
        
        return len(self.rate_limits[server_name]) < server.rate_limit
    
    async def list_resources(self, server_name: str) -> List[MCPResource]:
        """List available resources from an MCP server"""
        if not self.session:
            raise RuntimeError("MCP Client not initialized")
        
        server = self.servers.get(server_name)
        if not server or not server.enabled:
            return []
        
        if not self._check_rate_limit(server_name):
            logger.warning(f"Rate limit exceeded for {server_name}")
            return []
        
        try:
            url = f"{server.url}/resources"
            headers = {}
            if server.api_key:
                headers["Authorization"] = f"Bearer {server.api_key}"
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.rate_limits[server_name].append(datetime.now())
                    
                    resources = []
                    for resource_data in data.get("resources", []):
                        resource = MCPResource(
                            uri=resource_data["uri"],
                            name=resource_data["name"],
                            description=resource_data.get("description", ""),
                            mime_type=resource_data.get("mime_type", "application/json"),
                            metadata=resource_data.get("metadata", {})
                        )
                        resources.append(resource)
                    
                    logger.info(f"Listed {len(resources)} resources from {server_name}")
                    return resources
                else:
                    logger.error(f"Failed to list resources from {server_name}: {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Error listing resources from {server_name}: {e}")
            return []
    
    async def read_resource(self, server_name: str, resource_uri: str) -> Optional[Dict[str, Any]]:
        """Read a specific resource from an MCP server"""
        if not self.session:
            raise RuntimeError("MCP Client not initialized")
        
        server = self.servers.get(server_name)
        if not server or not server.enabled:
            return None
        
        if not self._check_rate_limit(server_name):
            logger.warning(f"Rate limit exceeded for {server_name}")
            return None
        
        try:
            url = f"{server.url}/resources/read"
            headers = {}
            if server.api_key:
                headers["Authorization"] = f"Bearer {server.api_key}"
            
            payload = {"uri": resource_uri}
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.rate_limits[server_name].append(datetime.now())
                    
                    logger.info(f"Read resource {resource_uri} from {server_name}")
                    return data
                else:
                    logger.error(f"Failed to read resource from {server_name}: {response.status}")
                    return None
        
        except Exception as e:
            logger.error(f"Error reading resource from {server_name}: {e}")
            return None
    
    async def search_resources(self, server_name: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for resources on an MCP server"""
        if not self.session:
            raise RuntimeError("MCP Client not initialized")
        
        server = self.servers.get(server_name)
        if not server or not server.enabled:
            return []
        
        if not self._check_rate_limit(server_name):
            logger.warning(f"Rate limit exceeded for {server_name}")
            return []
        
        try:
            url = f"{server.url}/resources/search"
            headers = {}
            if server.api_key:
                headers["Authorization"] = f"Bearer {server.api_key}"
            
            payload = {"query": query, "limit": limit}
            
            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.rate_limits[server_name].append(datetime.now())
                    
                    results = data.get("results", [])
                    logger.info(f"Found {len(results)} results for query '{query}' on {server_name}")
                    return results
                else:
                    logger.error(f"Failed to search resources on {server_name}: {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Error searching resources on {server_name}: {e}")
            return []

# Global MCP client instance
mcp_client = MCPClient()

# Default MCP servers for common integrations
def setup_default_mcp_servers():
    """Setup default MCP servers for common integrations"""
    
    # Product catalog server
    product_server = MCPServer(
        name="product_catalog",
        url="https://api.mcp.example.com/products",
        api_key=os.getenv("MCP_PRODUCT_API_KEY"),
        rate_limit=50,
        enabled=True
    )
    
    # Amazon product server
    amazon_server = MCPServer(
        name="amazon_products",
        url="https://api.mcp.example.com/amazon",
        api_key=os.getenv("MCP_AMAZON_API_KEY"),
        rate_limit=100,
        enabled=True
    )
    
    # Price tracking server
    price_server = MCPServer(
        name="price_tracking",
        url="https://api.mcp.example.com/prices",
        api_key=os.getenv("MCP_PRICE_API_KEY"),
        rate_limit=200,
        enabled=True
    )
    
    mcp_client.register_server(product_server)
    mcp_client.register_server(amazon_server)
    mcp_client.register_server(price_server)
