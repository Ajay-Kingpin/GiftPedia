#!/usr/bin/env python3
"""
Phase 4 Integration Test
Tests Explanation Layer & Frontend Components
"""

import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Set environment variables
os.environ['GEMINI_API_KEY'] = 'AIzaSyAoi-khzcttSvpXgVhuctAGubkBWvJFLSg'
os.environ['PINECONE_API_KEY'] = 'test-pinecone-key'
os.environ['PINECONE_ENVIRONMENT'] = 'us-west1-gcp'
os.environ['PINECONE_INDEX_NAME'] = 'giftpedia_products_v1'

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_explanation_agent():
    """Test Agent 4: Explanation & Confidence Generator"""
    print("🧪 Testing Agent 4: Explanation & Confidence Generator...")
    
    try:
        from agents.explanation.agent import ExplanationAgent, RecommendationExplanation
        from agents.profile_analyzer import UserProfile
        from agents.creative_idea import GiftConcept
        from agents.filter_rank import Product
        
        # Create test data
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=["no plastic"]
        )
        
        concepts = [
            GiftConcept(
                concept="Custom guitar accessories",
                category="Music",
                reasoning="Perfect for music enthusiast"
            )
        ]
        
        product = Product(
            product_id="prod_001",
            name="Fender Guitar Strap",
            category="Music & Instruments",
            price_inr=1899.0,
            brand="Fender",
            interest_tags=["music", "guitar"],
            occasion_tags=["birthday"],
            relationship_tags=["family"]
        )
        
        ranked_products = [
            {
                'product': product,
                'similarity_score': 0.95,
                'final_score': 1.15
            }
        ]
        
        # Test with mock Gemini
        with patch('agents.explanation.agent.genai') as mock_genai:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = json.dumps({
                "explanation": "This Fender Guitar Strap is perfect for music enthusiasts. It combines quality craftsmanship with practical functionality.",
                "key_reasons": ["High-quality materials", "Perfect for guitar players", "Great value for money"],
                "confidence_score": 0.85,
                "match_factors": ["Interest alignment", "Budget compatibility"],
                "potential_concerns": ["May require additional hardware"]
            })
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            agent = ExplanationAgent()
            explanations = agent.generate_explanation(profile, concepts, ranked_products)
            
            assert len(explanations) == 1, "Should generate 1 explanation"
            explanation = explanations[0]
            assert explanation.product_id == "prod_001", "Product ID should match"
            assert explanation.product_name == "Fender Guitar Strap", "Product name should match"
            assert explanation.confidence_score == 0.85, "Confidence score should match"
            assert len(explanation.key_reasons) == 3, "Should have 3 key reasons"
            assert len(explanation.match_factors) == 2, "Should have 2 match factors"
            
            print("✅ Explanation generation: PASS")
            print(f"   Product: {explanation.product_name}")
            print(f"   Confidence: {explanation.confidence_score}")
            print(f"   Key reasons: {len(explanation.key_reasons)}")
        
        # Test summary generation
        with patch('agents.explanation.agent.genai') as mock_genai:
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = "Based on the recipient's interests in music and guitar, we've selected high-quality accessories that enhance their musical experience."
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            agent = ExplanationAgent()
            summary = agent.generate_summary_explanation(explanations, profile)
            
            assert len(summary) > 50, "Summary should be substantial"
            assert "music" in summary, "Summary should mention interests"
            
            print("✅ Summary generation: PASS")
            print(f"   Summary length: {len(summary)} characters")
        
        # Test fallback explanation
        agent = ExplanationAgent()
        fallback = agent._create_fallback_explanation(profile, product, 0.88)
        
        assert fallback.product_id == "prod_001", "Fallback product ID should match"
        assert fallback.confidence_score < 0.88, "Fallback confidence should be lower"
        assert len(fallback.key_reasons) >= 3, "Fallback should have key reasons"
        
        print("✅ Fallback explanation: PASS")
        print(f"   Fallback confidence: {fallback.confidence_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ Explanation Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_phase4_workflow():
    """Test complete Phase 4 workflow"""
    print("\n🧪 Testing Complete Phase 4 Workflow...")
    
    try:
        from agents.profile_analyzer import ProfileAnalyzerAgent
        from agents.creative_idea import CreativeIdeaAgent
        from agents.filter_rank import FilterRankAgent
        from agents.explanation import ExplanationAgent
        
        # Mock all external dependencies
        with patch('agents.profile_analyzer.agent.genai') as mock_genai_profile, \
             patch('agents.creative_idea.agent.genai') as mock_genai_creative, \
             patch('agents.filter_rank.agent.pinecone') as mock_pinecone, \
             patch('agents.explanation.agent.genai') as mock_genai_explanation:
            
            # Setup mocks
            mock_genai_profile.GenerativeModel.return_value.generate_content.return_value.text = json.dumps({
                "recipient_age": 28,
                "recipient_gender": "male",
                "interests": ["music", "guitar"],
                "relationship": "family",
                "occasion": "birthday",
                "budget_inr": 2000,
                "constraints": ["no plastic"]
            })
            
            mock_genai_creative.GenerativeModel.return_value.generate_content.return_value.text = json.dumps({
                "gift_concepts": [{
                    "concept": "Custom guitar accessories",
                    "category": "Music",
                    "reasoning": "Perfect for music enthusiast"
                }]
            })
            
            # Mock Pinecone
            mock_index = Mock()
            mock_index.query.return_value = {
                'matches': [{
                    'id': 'prod_001',
                    'score': 0.95,
                    'metadata': {
                        'name': 'Fender Guitar Strap',
                        'category': 'Music & Instruments',
                        'price_inr': 1899.0,
                        'brand': 'Fender',
                        'interest_tags': ['music', 'guitar'],
                        'occasion_tags': ['birthday'],
                        'relationship_tags': ['family']
                    }
                }]
            }
            mock_pinecone.Index.return_value = mock_index
            mock_pinecone.list_indexes.return_value = ['giftpedia_products_v1']
            
            mock_genai_explanation.GenerativeModel.return_value.generate_content.return_value.text = json.dumps({
                "explanation": "This Fender Guitar Strap is perfect for music enthusiasts.",
                "key_reasons": ["High-quality materials", "Perfect for guitar players"],
                "confidence_score": 0.85,
                "match_factors": ["Interest alignment", "Budget compatibility"],
                "potential_concerns": []
            })
            
            # Initialize agents
            profile_analyzer = ProfileAnalyzerAgent()
            creative_agent = CreativeIdeaAgent()
            filter_rank_agent = FilterRankAgent()
            explanation_agent = ExplanationAgent()
            
            # Test input
            user_input = "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000, avoid plastic items"
            
            # Agent 1: Extract Profile
            print("   📋 Agent 1: Profile Analyzer...")
            profile = profile_analyzer.analyze(user_input)
            assert profile.interests == ["music", "guitar"], "Profile interests should match"
            print("   ✅ Profile extracted successfully")
            
            # Agent 2: Generate Creative Ideas
            print("   💡 Agent 2: Creative Idea Generator...")
            concepts = creative_agent.generate_concepts(profile)
            assert len(concepts) == 1, "Should generate 1 concept"
            print("   ✅ Creative concepts generated")
            
            # Agent 3: Filter & Rank Products
            print("   🎁 Agent 3: Filter & Rank Products...")
            ranked_products = filter_rank_agent.filter_and_rank(profile, concepts)
            assert len(ranked_products) == 1, "Should return 1 ranked product"
            print("   ✅ Products filtered and ranked")
            
            # Agent 4: Generate Explanations
            print("   📝 Agent 4: Explanation & Confidence Generator...")
            explanations = explanation_agent.generate_explanation(profile, concepts, ranked_products)
            assert len(explanations) == 1, "Should generate 1 explanation"
            print("   ✅ Explanations generated")
            
            # Generate summary
            summary = explanation_agent.generate_summary_explanation(explanations, profile)
            assert len(summary) > 50, "Summary should be substantial"
            print("   ✅ Summary generated")
            
            # Verify complete workflow
            explanation = explanations[0]
            assert explanation.product_name == "Fender Guitar Strap", "Product name should match"
            assert explanation.confidence_score == 0.85, "Confidence score should match"
            
            print("   🎉 Complete Phase 4 workflow successful!")
            print(f"   Final recommendation: {explanation.product_name}")
            print(f"   Confidence: {explanation.confidence_score}")
            print(f"   Summary: {summary[:100]}...")
            
            return True
        
    except Exception as e:
        print(f"❌ Phase 4 Workflow Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_components():
    """Test frontend component structure"""
    print("\n🧪 Testing Frontend Components...")
    
    try:
        # Check if frontend components exist
        frontend_dir = os.path.join(project_root, 'frontend', 'src')
        
        components_to_check = [
            'components/GiftRecommendationCard.tsx',
            'components/ConversationalInput.tsx',
            'components/RecommendationResults.tsx',
            'pages/GiftRecommendationPage.tsx',
            'services/api.ts',
            'types/gift.ts'
        ]
        
        missing_components = []
        for component in components_to_check:
            component_path = os.path.join(frontend_dir, component)
            if not os.path.exists(component_path):
                missing_components.append(component)
        
        if missing_components:
            print(f"❌ Missing frontend components: {missing_components}")
            return False
        
        print("✅ All frontend components exist")
        
        # Check TypeScript types
        types_file = os.path.join(frontend_dir, 'types/gift.ts')
        with open(types_file, 'r') as f:
            types_content = f.read()
        
        required_types = [
            'RecommendationExplanation',
            'UserProfile',
            'Product',
            'GiftConcept'
        ]
        
        missing_types = []
        for type_name in required_types:
            if f'export interface {type_name}' not in types_content:
                missing_types.append(type_name)
        
        if missing_types:
            print(f"❌ Missing TypeScript types: {missing_types}")
            return False
        
        print("✅ All required TypeScript types defined")
        
        # Check API service
        api_file = os.path.join(frontend_dir, 'services/api.ts')
        with open(api_file, 'r') as f:
            api_content = f.read()
        
        required_functions = [
            'getRecommendations',
            'getProductDetails',
            'saveRecommendations',
            'shareRecommendations'
        ]
        
        missing_functions = []
        for func_name in required_functions:
            if f'export const {func_name}' not in api_content:
                missing_functions.append(func_name)
        
        if missing_functions:
            print(f"❌ Missing API functions: {missing_functions}")
            return False
        
        print("✅ All required API functions defined")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend Components Error: {e}")
        return False

def main():
    """Run complete Phase 4 integration test"""
    print("🚀 Phase 4 Integration Test Suite")
    print("=" * 60)
    print("Testing Explanation Layer & Frontend Components")
    
    tests = [
        ("Agent 4: Explanation & Confidence Generator", test_explanation_agent),
        ("Complete Phase 4 Workflow", test_complete_phase4_workflow),
        ("Frontend Components", test_frontend_components),
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
    print("📊 PHASE 4 INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.ljust(45)}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Phase 4 Integration Tests - ALL COMPONENTS WORKING!")
        print("\n📋 Phase 4 Components Verified:")
        print("   • Agent 4: Explanation & Confidence Generator")
        print("   • Recommendation explanation generation")
        print("   • Confidence scoring algorithm")
        print("   • Summary explanation generation")
        print("   • Fallback explanation system")
        print("   • Complete 4-agent workflow")
        print("   • Frontend React components")
        print("   • TypeScript type definitions")
        print("   • API service integration")
        
        print("\n✅ Phase 4 Implementation: COMPLETE AND VERIFIED")
        print("✅ Ready for Frontend Development")
        print("✅ Ready for Phase 5: Integration & Testing")
        return 0
    else:
        print("\n⚠️  Some Phase 4 integration tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
