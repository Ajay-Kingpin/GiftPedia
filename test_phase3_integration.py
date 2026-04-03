#!/usr/bin/env python3
"""
Phase 3 Integration Test
Tests Vector Database Integration with all components
"""

import os
import sys

# Set environment variables
os.environ['GEMINI_API_KEY'] = 'AIzaSyAoi-khzcttSvpXgVhuctAGubkBWvJFLSg'
os.environ['PINECONE_API_KEY'] = 'test-pinecone-key'
os.environ['PINECONE_ENVIRONMENT'] = 'us-west1-gcp'
os.environ['PINECONE_INDEX_NAME'] = 'giftpedia_products_v1'

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_embedding_service():
    """Test embedding service functionality"""
    print("🧪 Testing Embedding Service...")
    
    try:
        from services.embedding_service import embedding_service
        
        # Test text embedding
        text = "Fender guitar strap for music lovers"
        embedding = embedding_service.generate_embedding(text)
        
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        
        # Test product embedding
        product = {
            "name": "Fender Guitar Strap",
            "category": "Music & Instruments",
            "subcategory": "Guitar Accessories",
            "brand": "Fender",
            "interest_tags": ["music", "guitar", "accessory"],
            "occasion_tags": ["birthday"],
            "relationship_tags": ["friend"]
        }
        
        product_embedding = embedding_service.generate_product_embedding(product)
        print(f"✅ Generated product embedding: {len(product_embedding)} dimensions")
        
        # Test batch embedding
        texts = ["guitar music", "cooking gardening", "fitness yoga"]
        batch_embeddings = embedding_service.batch_generate_embeddings(texts)
        print(f"✅ Generated batch embeddings: {len(batch_embeddings)} texts")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding Service Error: {e}")
        return False

def test_pinecone_service():
    """Test Pinecone service functionality"""
    print("\n🧪 Testing Pinecone Service...")
    
    try:
        from services.pinecone_service import pinecone_service
        
        # Test index stats
        stats = pinecone_service.get_index_stats()
        print(f"✅ Pinecone index stats: {stats}")
        
        # Test sample data initialization
        product_ids = pinecone_service.initialize_sample_data()
        print(f"✅ Initialized {len(product_ids)} sample products")
        
        # Test product search
        query_embedding = embedding_service.generate_embedding("music guitar accessories")
        results = pinecone_service.search_products(query_embedding, top_k=3)
        print(f"✅ Found {len(results)} products for 'music guitar accessories'")
        
        # Test product retrieval
        if product_ids:
            product = pinecone_service.get_product_by_id(product_ids[0])
            if product:
                print(f"✅ Retrieved product: {product['metadata']['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pinecone Service Error: {e}")
        print("Note: This is expected if Pinecone credentials are not configured")
        return False

def test_filter_rank_agent():
    """Test Filter & Rank agent functionality"""
    print("\n🧪 Testing Filter & Rank Agent...")
    
    try:
        from agents import FilterRankAgent, UserProfile, GiftConcept
        
        # Mock Pinecone for testing
        import unittest.mock
        with unittest.mock.patch('agents.filter_rank.agent.pinecone') as mock_pinecone:
            mock_pinecone.list_indexes.return_value = ['giftpedia_products_v1']
            mock_index = unittest.mock.Mock()
            mock_pinecone.Index.return_value = mock_index
            
            # Mock search response
            mock_index.query.return_value = {
                'matches': [
                    {
                        'id': 'prod_001',
                        'score': 0.95,
                        'values': [0.1] * 1536,
                        'metadata': {
                            'name': 'Fender Guitar Strap',
                            'category': 'Music & Instruments',
                            'price_inr': 1899.0,
                            'brand': 'Fender',
                            'interest_tags': ['music', 'guitar'],
                            'occasion_tags': ['birthday'],
                            'relationship_tags': ['family'],
                            'is_active': True
                        }
                    },
                    {
                        'id': 'prod_002',
                        'score': 0.85,
                        'values': [0.2] * 1536,
                        'metadata': {
                            'name': 'Plastic Guitar Pick',
                            'category': 'Music & Instruments',
                            'price_inr': 100.0,
                            'brand': 'Generic',
                            'interest_tags': ['music'],
                            'occasion_tags': ['birthday'],
                            'relationship_tags': ['friend'],
                            'is_active': True
                        }
                    }
                ]
            }
            
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
                    concept="Custom guitar accessories",
                    category="Music",
                    reasoning="Perfect for music enthusiast"
                )
            ]
            
            # Test filter and rank
            results = agent.filter_and_rank(profile, concepts)
            print(f"✅ Filtered and ranked {len(results)} products")
            
            # Should only return non-plastic product
            assert len(results) == 1
            assert results[0]['product'].name == "Fender Guitar Strap"
            print(f"✅ Top product: {results[0]['product'].name} (Score: {results[0]['final_score']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Filter & Rank Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_phase3_workflow():
    """Test complete Phase 3 workflow"""
    print("\n🧪 Testing Complete Phase 3 Workflow...")
    print("=" * 60)
    
    try:
        from agents import ProfileAnalyzerAgent, CreativeIdeaAgent, FilterRankAgent, UserProfile, GiftConcept
        
        # Mock Pinecone for testing
        import unittest.mock
        with unittest.mock.patch('agents.filter_rank.agent.pinecone') as mock_pinecone:
            mock_pinecone.list_indexes.return_value = ['giftpedia_products_v1']
            mock_index = unittest.mock.Mock()
            mock_pinecone.Index.return_value = mock_index
            
            # Mock search response
            mock_index.query.return_value = {
                'matches': [
                    {
                        'id': 'prod_001',
                        'score': 0.95,
                        'values': [0.1] * 1536,
                        'metadata': {
                            'name': 'Fender Guitar Strap',
                            'category': 'Music & Instruments',
                            'price_inr': 1899.0,
                            'brand': 'Fender',
                            'interest_tags': ['music', 'guitar'],
                            'occasion_tags': ['birthday'],
                            'relationship_tags': ['family'],
                            'is_active': True
                        }
                    }
                ]
            }
            
            # Initialize agents
            profile_analyzer = ProfileAnalyzerAgent()
            creative_idea_agent = CreativeIdeaAgent()
            filter_rank_agent = FilterRankAgent()
            
            # Test input
            user_input = "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
            print(f"📝 User Input: {user_input}")
            
            # Agent 1: Extract Profile
            print("\n📋 Agent 1: Profile Analyzer...")
            profile = profile_analyzer.analyze(user_input)
            print(f"✅ Profile extracted: Age={profile.recipient_age}, Interests={profile.interests}")
            
            # Agent 2: Generate Creative Ideas
            print("\n💡 Agent 2: Creative Idea Generator...")
            concepts = creative_idea_agent.generate_concepts(profile)
            print(f"✅ Generated {len(concepts)} creative concepts")
            
            # Agent 3: Filter & Rank Products
            print("\n🎁 Agent 3: Filter & Rank Products...")
            ranked_products = filter_rank_agent.filter_and_rank(profile, concepts)
            print(f"✅ Filtered and ranked {len(ranked_products)} products")
            
            # Display results
            if ranked_products:
                top_product = ranked_products[0]
                product = top_product['product']
                print(f"\n🎯 Top Recommendation:")
                print(f"   Product: {product.name}")
                print(f"   Price: ₹{product.price_inr}")
                print(f"   Category: {product.category}")
                print(f"   Similarity Score: {top_product['similarity_score']:.3f}")
                print(f"   Final Score: {top_product['final_score']:.3f}")
            
            print("\n🎉 Complete Phase 3 workflow successful!")
            return True
            
    except Exception as e:
        print(f"❌ Phase 3 Workflow Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Phase 3 integration tests"""
    print("🚀 Phase 3 Integration Test")
    print("=" * 60)
    
    tests = [
        ("Embedding Service", test_embedding_service),
        ("Pinecone Service", test_pinecone_service),
        ("Filter & Rank Agent", test_filter_rank_agent),
        ("Complete Phase 3 Workflow", test_complete_phase3_workflow),
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
    print("📊 PHASE 3 INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.ljust(25)}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Phase 3 Integration is COMPLETE and WORKING!")
        print("✅ Embedding service functional")
        print("✅ Pinecone service functional")
        print("✅ Filter & Rank agent functional")
        print("✅ Complete workflow (Agent 1 → Agent 2 → Agent 3) working")
        print("✅ Ready for Phase 4: Explanation Layer & Frontend")
        return 0
    else:
        print("⚠️  Some Phase 3 tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
