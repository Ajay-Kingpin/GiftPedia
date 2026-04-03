"""
End-to-End Integration Tests
Tests complete gift recommendation workflow
"""

import os
import sys
import time
import json
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from orchestration import GiftRecommendationOrchestrator, RecommendationRequest
from agents import UserProfile, GiftConcept, Product

class TestEndToEndWorkflow:
    """Test complete end-to-end workflow"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return GiftRecommendationOrchestrator()
    
    @pytest.fixture
    def sample_request(self):
        """Sample recommendation request"""
        return RecommendationRequest(
            user_input="I need a birthday gift for my brother who is 28 years old, loves music and guitar, budget is ₹2000, avoid plastic items",
            max_recommendations=3
        )
    
    def test_complete_workflow_success(self, orchestrator, sample_request):
        """Test complete successful workflow"""
        # Process request
        response = orchestrator.get_recommendations(sample_request)
        
        # Verify response structure
        assert response.profile is not None
        assert response.concepts is not None
        assert response.recommendations is not None
        assert response.explanations is not None
        assert response.summary is not None
        assert response.processing_time > 0
        assert response.session_id is not None
        assert response.timestamp is not None
        
        # Verify profile
        profile = response.profile
        assert profile.recipient_age == 28
        assert profile.recipient_gender == "male"
        assert "music" in profile.interests
        assert "guitar" in profile.interests
        assert profile.relationship == "family"
        assert profile.occasion == "birthday"
        assert profile.budget_inr == 2000
        assert "plastic" in profile.constraints
        
        # Verify concepts
        concepts = response.concepts
        assert len(concepts) > 0
        for concept in concepts:
            assert isinstance(concept, GiftConcept)
            assert concept.concept is not None
            assert concept.category is not None
            assert concept.reasoning is not None
        
        # Verify recommendations
        recommendations = response.recommendations
        assert len(recommendations) <= sample_request.max_recommendations
        for rec in recommendations:
            assert 'product_id' in rec
            assert 'name' in rec
            assert 'price_inr' in rec
            assert 'similarity_score' in rec
            assert 'final_score' in rec
        
        # Verify explanations
        explanations = response.explanations
        assert len(explanations) == len(recommendations)
        for explanation in explanations:
            assert explanation.product_id is not None
            assert explanation.product_name is not None
            assert explanation.explanation is not None
            assert len(explanation.key_reasons) >= 2
            assert 0.0 <= explanation.confidence_score <= 1.0
            assert len(explanation.match_factors) >= 1
        
        # Verify summary
        assert len(response.summary) > 50
        assert "music" in response.summary.lower()
        assert "birthday" in response.summary.lower()
        
        # Verify processing time is reasonable
        assert response.processing_time < 30.0  # Should complete within 30 seconds
        
        print(f"✅ Complete workflow test passed in {response.processing_time:.2f}s")
    
    def test_multiple_requests_performance(self, orchestrator):
        """Test performance with multiple requests"""
        requests = [
            RecommendationRequest(
                user_input=f"Gift for sister who loves reading, budget ₹{1000 + i*500}, birthday",
                max_recommendations=2
            )
            for i in range(5)
        ]
        
        processing_times = []
        
        for i, request in enumerate(requests):
            start_time = time.time()
            response = orchestrator.get_recommendations(request)
            end_time = time.time()
            
            processing_times.append(response.processing_time)
            
            # Verify each request succeeded
            assert response.recommendations is not None
            assert len(response.recommendations) <= request.max_recommendations
            assert response.explanations is not None
            
            print(f"Request {i+1}: {response.processing_time:.2f}s")
        
        # Verify performance consistency
        avg_time = sum(processing_times) / len(processing_times)
        max_time = max(processing_times)
        
        assert avg_time < 20.0, f"Average processing time too high: {avg_time:.2f}s"
        assert max_time < 30.0, f"Max processing time too high: {max_time:.2f}s"
        
        print(f"✅ Performance test passed - Avg: {avg_time:.2f}s, Max: {max_time:.2f}s")
    
    def test_error_handling(self, orchestrator):
        """Test error handling in various scenarios"""
        # Test with invalid input
        invalid_request = RecommendationRequest(
            user_input="",  # Empty input
            max_recommendations=3
        )
        
        response = orchestrator.get_recommendations(invalid_request)
        
        # Should still return a response (with error handling)
        assert response is not None
        assert response.profile is not None
        assert response.summary is not None
        assert "error" in response.metadata or len(response.recommendations) == 0
        
        print("✅ Error handling test passed")
    
    def test_concurrent_requests(self, orchestrator):
        """Test handling of concurrent requests"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def process_request(request_id):
            """Process a single request"""
            request = RecommendationRequest(
                user_input=f"Gift for friend who loves sports, budget ₹1500, birthday - Request {request_id}",
                max_recommendations=2
            )
            
            try:
                response = orchestrator.get_recommendations(request)
                results.put((request_id, response, None))
            except Exception as e:
                results.put((request_id, None, e))
        
        # Start multiple concurrent requests
        threads = []
        num_requests = 3
        
        for i in range(num_requests):
            thread = threading.Thread(target=process_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        successful_requests = 0
        failed_requests = 0
        
        while not results.empty():
            request_id, response, error = results.get()
            
            if error:
                failed_requests += 1
                print(f"Request {request_id} failed: {error}")
            else:
                successful_requests += 1
                assert response is not None
                assert response.recommendations is not None
        
        # At least some requests should succeed
        assert successful_requests > 0, "No concurrent requests succeeded"
        
        print(f"✅ Concurrent requests test passed - Success: {successful_requests}, Failed: {failed_requests}")
    
    def test_performance_metrics(self, orchestrator):
        """Test performance metrics collection"""
        # Process a few requests to generate metrics
        for i in range(3):
            request = RecommendationRequest(
                user_input=f"Gift for dad who loves technology, budget ₹{2000 + i*500}, anniversary",
                max_recommendations=2
            )
            orchestrator.get_recommendations(request)
        
        # Get metrics
        metrics = orchestrator.get_performance_metrics()
        
        # Verify metrics structure
        assert 'total_requests' in metrics
        assert 'successful_requests' in metrics
        assert 'failed_requests' in metrics
        assert 'average_processing_time' in metrics
        assert 'success_rate' in metrics
        assert 'agent_performance' in metrics
        
        # Verify metrics values
        assert metrics['total_requests'] >= 3
        assert metrics['successful_requests'] >= 0
        assert metrics['average_processing_time'] > 0
        assert 0 <= metrics['success_rate'] <= 1
        
        # Verify agent metrics
        agent_metrics = metrics['agent_performance']
        for agent_name in ['profile_analyzer', 'creative_idea', 'filter_rank', 'explanation']:
            assert agent_name in agent_metrics
            assert 'avg_time' in agent_metrics[agent_name]
            assert 'success_rate' in agent_metrics[agent_name]
        
        print(f"✅ Performance metrics test passed - Total requests: {metrics['total_requests']}")
    
    def test_health_check(self, orchestrator):
        """Test health check functionality"""
        health = orchestrator.health_check()
        
        # Verify health check structure
        assert 'overall_status' in health
        assert 'agents' in health
        assert 'timestamp' in health
        assert 'performance_metrics' in health
        
        # Verify agent health
        agents = health['agents']
        expected_agents = ['profile_analyzer', 'creative_idea', 'filter_rank', 'explanation']
        
        for agent in expected_agents:
            assert agent in agents
            assert 'status' in agents[agent]
        
        # Overall status should be healthy or degraded
        assert health['overall_status'] in ['healthy', 'degraded', 'unhealthy']
        
        print(f"✅ Health check test passed - Status: {health['overall_status']}")

class TestAPIServer:
    """Test API server endpoints"""
    
    @pytest.fixture
    def api_client(self):
        """Create API test client"""
        from fastapi.testclient import TestClient
        from api.main import app
        
        return TestClient(app)
    
    def test_root_endpoint(self, api_client):
        """Test root endpoint"""
        response = api_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "GiftPedia API"
        assert data["status"] == "running"
        
        print("✅ Root endpoint test passed")
    
    def test_health_endpoint(self, api_client):
        """Test health check endpoint"""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "agents" in data
        assert "performance_metrics" in data
        
        print("✅ Health endpoint test passed")
    
    def test_recommendations_endpoint(self, api_client):
        """Test recommendations endpoint"""
        request_data = {
            "user_input": "I need a birthday gift for my brother who is 28 years old, loves music and guitar, budget is ₹2000",
            "max_recommendations": 3
        }
        
        response = api_client.post("/recommendations", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        assert "processing_time" in data
        assert "session_id" in data
        assert "timestamp" in data
        
        # Verify response data structure
        response_data = data["data"]
        assert "profile" in response_data
        assert "concepts" in response_data
        assert "recommendations" in response_data
        assert "explanations" in response_data
        assert "summary" in response_data
        
        print("✅ Recommendations endpoint test passed")
    
    def test_recommendations_endpoint_error(self, api_client):
        """Test recommendations endpoint with error"""
        request_data = {
            "user_input": "x" * 2000,  # Too long input
            "max_recommendations": 3
        }
        
        response = api_client.post("/recommendations", json=request_data)
        
        # Should handle error gracefully
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is False
            assert "error" in data
        
        print("✅ Recommendations error handling test passed")
    
    def test_categories_endpoint(self, api_client):
        """Test categories endpoint"""
        response = api_client.get("/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        for category in data:
            assert "id" in category
            assert "name" in category
            assert "product_count" in category
        
        print("✅ Categories endpoint test passed")
    
    def test_metrics_endpoint(self, api_client):
        """Test metrics endpoint"""
        response = api_client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_requests" in data
        assert "successful_requests" in data
        assert "average_processing_time" in data
        
        print("✅ Metrics endpoint test passed")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
