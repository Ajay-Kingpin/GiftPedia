#!/usr/bin/env python3
"""
Test FAISS Integration
Tests the new FAISS-based vector store and Filter & Rank Agent
"""

import os
import sys
import json
import numpy as np
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_vector_store():
    """Test FAISS vector store"""
    print("🧪 Testing FAISS Vector Store...")
    
    try:
        from services.vector_store import FAISSVectorStore, create_sample_products, initialize_vector_store
        
        # Initialize vector store
        initialize_vector_store()
        
        # Get stats
        stats = vector_store.get_stats()
        print(f"✅ Vector Store Stats: {json.dumps(stats, indent=2)}")
        
        # Test search
        query_embedding = np.random.rand(1536).tolist()
        results = vector_store.search_similar(query_embedding, k=3)
        
        print(f"✅ Search Results: {len(results)} products found")
        for result in results:
            print(f"   - {result['name']} (Similarity: {result['similarity_score']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector Store Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_faiss_filter_rank():
    """Test FAISS-based Filter & Rank Agent"""
    print("\n🧪 Testing FAISS Filter & Rank Agent...")
    
    try:
        from agents.filter_rank.faiss_agent import FilterRankAgent, UserProfile, GiftConcept
        
        # Create agent
        agent = FilterRankAgent()
        
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

def test_complete_workflow():
    """Test complete workflow with FAISS"""
    print("\n🧪 Testing Complete Workflow with FAISS...")
    
    try:
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
        
        # Test Filter & Rank with FAISS
        print("🎁 Testing Filter & Rank with FAISS...")
        filter_rank = FilterRankAgent()
        recommendations = filter_rank.filter_and_rank_products(profile, concepts, max_recommendations=3)
        print(f"✅ Filtered and ranked {len(recommendations)} products")
        
        # Test Explanation Agent
        print("📝 Testing Explanation Agent...")
        explanation_agent = ExplanationAgent()
        explanations = explanation_agent.generate_explanation(profile, concepts, recommendations)
        print(f"✅ Generated {len(explanations)} explanations")
        
        print("\n🎉 Complete FAISS workflow successful!")
        return True
        
    except Exception as e:
        print(f"❌ Complete Workflow Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_integration():
    """Test API integration with FAISS"""
    print("\n🧪 Testing API Integration with FAISS...")
    
    try:
        import requests
        import time
        
        # Test health endpoint
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
        
        # Test recommendations endpoint
        request_data = {
            "user_input": "Birthday gift for brother who loves music, budget ₹2000",
            "max_recommendations": 3
        }
        
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
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API Connection Error: {e}")
        print("💡 Make sure the API server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ API Integration Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all FAISS integration tests"""
    print("🚀 FAISS Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("FAISS Vector Store", test_vector_store),
        ("FAISS Filter & Rank Agent", test_faiss_filter_rank),
        ("Complete Workflow", test_complete_workflow),
        ("API Integration", test_api_integration)
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
    print("📊 FAISS INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.ljust(35)}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 FAISS Integration - ALL TESTS PASSING!")
        print("\n✅ Benefits of FAISS over Pinecone:")
        print("   • Free and open source")
        print("   • No login or API keys required")
        print("   • Local storage - no external dependencies")
        print("   • Fast vector search (L2 distance)")
        print("   • Persistent storage on disk")
        print("   • Easy to deploy and scale")
        
        print("\n🚀 Ready for production with FAISS!")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
