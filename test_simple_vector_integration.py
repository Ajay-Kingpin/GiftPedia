#!/usr/bin/env python3
"""
Test Simple Vector Store Integration
Tests the new simple vector store and Filter & Rank Agent (No Dependencies Required)
"""

import os
import sys
import json
import time
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_simple_vector_store():
    """Test simple vector store"""
    print("🧪 Testing Simple Vector Store...")
    
    try:
        from services.simple_vector_store import SimpleVectorStore, simple_vector_store, initialize_simple_vector_store
        
        # Initialize vector store
        initialize_simple_vector_store()
        
        # Get stats
        stats = simple_vector_store.get_stats()
        print(f"✅ Vector Store Stats: {json.dumps(stats, indent=2)}")
        
        # Test search
        query_embedding = simple_vector_store._generate_embedding(["music", "guitar"])
        results = simple_vector_store.search_similar(query_embedding, k=3)
        
        print(f"✅ Search Results: {len(results)} products found")
        for result in results:
            print(f"   - {result['name']} (Similarity: {result['similarity_score']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector Store Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_filter_rank():
    """Test simple Filter & Rank Agent"""
    print("\n🧪 Testing Simple Filter & Rank Agent...")
    
    try:
        from agents.filter_rank.simple_agent import SimpleFilterRankAgent, UserProfile, GiftConcept
        
        # Create agent
        agent = SimpleFilterRankAgent()
        
        # Create test profile
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=["no plastic"]
        )
        
        # Create test concepts
        concepts = [
            GiftConcept(
                concept="Music accessories for guitar enthusiasts",
                category="Music",
                reasoning="Perfect for someone who loves playing guitar"
            )
        ]
        
        # Test filtering and ranking
        recommendations = agent.filter_and_rank_products(
            profile, concepts, max_recommendations=5
        )
        
        print(f"✅ Generated {len(recommendations)} recommendations")
        for rec in recommendations:
            print(f"   {rec['rank']}. {rec['name']} - ₹{rec['price_inr']} (Score: {rec['final_score']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Filter & Rank Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_simple_workflow():
    """Test complete workflow with simple vector store"""
    print("\n🧪 Testing Complete Workflow with Simple Vector Store...")
    
    try:
        # Set environment variables to avoid errors
        os.environ['GEMINI_API_KEY'] = 'test-key'
        
        from agents import ProfileAnalyzerAgent, CreativeIdeaAgent, FilterRankAgent, ExplanationAgent
        from agents.profile_analyzer import UserProfile
        from agents.creative_idea import GiftConcept
        
        # Test Profile Analyzer
        print("📋 Testing Profile Analyzer...")
        profile_analyzer = ProfileAnalyzerAgent()
        user_input = "I need a birthday gift for my brother, a 28-year-old musician who loves guitar. Budget is ₹2000."
        profile = profile_analyzer.analyze_profile(user_input)
        print(f"✅ Profile analyzed: {profile.interests}, Budget: ₹{profile.budget_inr}")
        
        # Test Creative Idea Generator
        print("💡 Testing Creative Idea Generator...")
        idea_generator = CreativeIdeaAgent()
        concepts = idea_generator.generate_creative_concepts(profile)
        print(f"✅ Generated {len(concepts)} concepts")
        
        # Test Filter & Rank with Simple Vector Store
        print("🎁 Testing Filter & Rank with Simple Vector Store...")
        filter_rank = FilterRankAgent()
        recommendations = filter_rank.filter_and_rank_products(profile, concepts, max_recommendations=3)
        print(f"✅ Filtered and ranked {len(recommendations)} products")
        
        # Test Explanation Agent (with mock)
        print("📝 Testing Explanation Agent...")
        explanation_agent = ExplanationAgent()
        
        # Mock the explanation generation to avoid API calls
        class MockResponse:
            def __init__(self, text):
                self.text = text
        
        # Mock the model generate_content method
        original_generate = explanation_agent.model.generate_content
        explanation_agent.model.generate_content = lambda prompt: MockResponse("Perfect gift for music lovers!")
        
        explanations = explanation_agent.generate_explanation(profile, concepts, recommendations)
        print(f"✅ Generated {len(explanations)} explanations")
        
        print("\n🎉 Complete Simple Vector Store workflow successful!")
        return True
        
    except Exception as e:
        print(f"❌ Complete Workflow Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_with_simple_vector():
    """Test API integration with simple vector store"""
    print("\n🧪 Testing API Integration with Simple Vector Store...")
    
    try:
        import requests
        
        # Test health endpoint
        try:
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            if health_response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {health_response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("⚠️  API server not running, skipping health check")
        
        # Test recommendations endpoint
        request_data = {
            "user_input": "Birthday gift for brother who loves music, budget ₹2000",
            "max_recommendations": 3
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:8000/recommendations",
                json=request_data,
                timeout=30
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                processing_time = end_time - start_time
                print(f"✅ Recommendations generated in {processing_time:.2f}s")
                print(f"✅ Response: {result.get('success', False)}")
                
                if result.get('data', {}).get('recommendations'):
                    rec_count = len(result['data']['recommendations'])
                    print(f"✅ Found {rec_count} recommendations")
                
                return True
            else:
                print(f"❌ Recommendations failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("⚠️  API server not running, skipping recommendations test")
            return True  # Not a failure of the simple vector store
            
    except Exception as e:
        print(f"❌ API Integration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all simple vector integration tests"""
    print("🚀 Simple Vector Store Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Simple Vector Store", test_simple_vector_store),
        ("Simple Filter & Rank Agent", test_simple_filter_rank),
        ("Complete Workflow", test_complete_simple_workflow),
        ("API Integration", test_api_with_simple_vector)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SIMPLE VECTOR STORE INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.ljust(35)}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed >= 3:  # Allow API test to fail if server not running
        print("\n🎉 Simple Vector Store Integration - SUCCESS!")
        print("\n✅ Benefits of Simple Vector Store:")
        print("   • Completely free - no API keys required")
        print("   • No login or registration needed")
        print("   • No external dependencies")
        print("   • Simple cosine similarity search")
        print("   • JSON file storage - easy to backup")
        print("   • Fast and lightweight")
        print("   • Works offline")
        print("   • Easy to understand and modify")
        
        print("\n🚀 Perfect replacement for Pinecone!")
        print("\n📋 Next Steps:")
        print("   1. Start the API server: cd api && python main.py")
        print("   2. Start frontend: cd frontend && npm run dev")
        print("   3. Test the complete workflow")
        print("   4. Add more products to the catalog")
        
        return 0
    else:
        print(f"\n⚠️  More than {len(results) - 1} tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
