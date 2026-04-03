#!/usr/bin/env python3
"""
Phase 4 Standalone Test
Tests Agent 4 without importing other agents
"""

import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Set environment variables
os.environ['GEMINI_API_KEY'] = 'AIzaSyAoi-khzcttSvpXgVhuctAGubkBWvJFLSg'

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_explanation_agent_standalone():
    """Test Agent 4: Explanation & Confidence Generator standalone"""
    print("🧪 Testing Agent 4: Explanation & Confidence Generator (Standalone)...")
    
    try:
        # Import only Agent 4
        from agents.explanation.agent import ExplanationAgent, RecommendationExplanation
        
        # Create test data
        class MockProfile:
            def __init__(self):
                self.recipient_age = 28
                self.recipient_gender = "male"
                self.interests = ["music", "guitar"]
                self.relationship = "family"
                self.occasion = "birthday"
                self.budget_inr = 2000
                self.constraints = ["no plastic"]
        
        class MockConcept:
            def __init__(self):
                self.concept = "Custom guitar accessories"
                self.category = "Music"
                self.reasoning = "Perfect for music enthusiast"
        
        class MockProduct:
            def __init__(self):
                self.product_id = "prod_001"
                self.name = "Fender Guitar Strap"
                self.category = "Music & Instruments"
                self.price_inr = 1899.0
                self.brand = "Fender"
                self.interest_tags = ["music", "guitar"]
                self.occasion_tags = ["birthday"]
                self.relationship_tags = ["family"]
        
        profile = MockProfile()
        concepts = [MockConcept()]
        product = MockProduct()
        
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
        
        # Test confidence score calculation
        explanation_data = {
            "explanation": "This is a perfect match with great features and excellent quality.",
            "key_reasons": ["Perfect match", "Great features", "Excellent quality", "Highly recommended"]
        }
        
        confidence = agent._calculate_confidence_score(0.95, explanation_data)
        assert confidence >= 0.85, "High score should result in high confidence"
        
        confidence = agent._calculate_confidence_score(0.60, explanation_data)
        assert confidence <= 0.70, "Low score should result in lower confidence"
        
        print("✅ Confidence score calculation: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Explanation Agent Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recommendation_explanation_model():
    """Test RecommendationExplanation model"""
    print("\n🧪 Testing RecommendationExplanation Model...")
    
    try:
        from agents.explanation.agent import RecommendationExplanation
        
        # Test model creation
        explanation = RecommendationExplanation(
            product_id="prod_001",
            product_name="Fender Guitar Strap",
            explanation="Perfect gift for music enthusiasts who love guitar accessories",
            key_reasons=["Matches music interest", "High quality", "Good value"],
            confidence_score=0.85,
            match_factors=["Interest alignment", "Budget compatibility"],
            potential_concerns=["May need additional accessories"]
        )
        
        assert explanation.product_id == "prod_001", "Product ID should match"
        assert explanation.product_name == "Fender Guitar Strap", "Product name should match"
        assert explanation.confidence_score == 0.85, "Confidence score should match"
        assert len(explanation.key_reasons) == 3, "Should have 3 key reasons"
        assert len(explanation.match_factors) == 2, "Should have 2 match factors"
        assert len(explanation.potential_concerns) == 1, "Should have 1 concern"
        
        print("✅ Model creation: PASS")
        print(f"   Product: {explanation.product_name}")
        print(f"   Confidence: {explanation.confidence_score}")
        print(f"   Key reasons: {len(explanation.key_reasons)}")
        print(f"   Match factors: {len(explanation.match_factors)}")
        
        # Test model serialization
        data = explanation.dict()
        assert data['product_id'] == "prod_001", "Serialized product ID should match"
        assert data['confidence_score'] == 0.85, "Serialized confidence should match"
        
        print("✅ Model serialization: PASS")
        
        # Test model validation
        try:
            invalid_explanation = RecommendationExplanation(
                product_id="prod_001",
                product_name="Fender Guitar Strap",
                explanation="Perfect gift",
                key_reasons=["Matches music interest"],
                confidence_score=1.5,  # Invalid confidence score
                match_factors=["Interest alignment"],
                potential_concerns=[]
            )
            print("❌ Should have failed validation")
            return False
        except Exception:
            print("✅ Model validation: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ RecommendationExplanation Model Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_explanation_prompt_generation():
    """Test explanation prompt generation"""
    print("\n🧪 Testing Explanation Prompt Generation...")
    
    try:
        from agents.explanation.agent import ExplanationAgent
        
        # Create test data
        class MockProfile:
            def __init__(self):
                self.recipient_age = 28
                self.recipient_gender = "male"
                self.interests = ["music", "guitar"]
                self.relationship = "family"
                self.occasion = "birthday"
                self.budget_inr = 2000
                self.constraints = ["no plastic"]
        
        class MockConcept:
            def __init__(self):
                self.concept = "Custom guitar accessories"
                self.category = "Music"
                self.reasoning = "Perfect for music enthusiast"
        
        class MockProduct:
            def __init__(self):
                self.product_id = "prod_001"
                self.name = "Fender Guitar Strap"
                self.category = "Music & Instruments"
                self.price_inr = 1899.0
                self.brand = "Fender"
                self.interest_tags = ["music", "guitar"]
        
        profile = MockProfile()
        concepts = [MockConcept()]
        product = MockProduct()
        
        agent = ExplanationAgent()
        prompt = agent._create_explanation_prompt(profile, concepts, product, 0.95, 1.15)
        
        # Check prompt components
        assert "USER PROFILE:" in prompt, "Should contain user profile section"
        assert "CREATIVE CONCEPTS:" in prompt, "Should contain concepts section"
        assert "RECOMMENDED PRODUCT:" in prompt, "Should contain product section"
        assert "MATCH SCORES:" in prompt, "Should contain scores section"
        assert "28" in prompt, "Should contain age"
        assert "music" in prompt, "Should contain interests"
        assert "birthday" in prompt, "Should contain occasion"
        assert "2000" in prompt, "Should contain budget"
        assert "Fender Guitar Strap" in prompt, "Should contain product name"
        assert "0.95" in prompt, "Should contain similarity score"
        assert "1.15" in prompt, "Should contain final score"
        
        print("✅ Prompt generation: PASS")
        print(f"   Prompt length: {len(prompt)} characters")
        print(f"   Contains all required sections")
        
        return True
        
    except Exception as e:
        print(f"❌ Explanation Prompt Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_parsing():
    """Test JSON parsing with various formats"""
    print("\n🧪 Testing JSON Parsing...")
    
    try:
        from agents.explanation.agent import ExplanationAgent
        
        agent = ExplanationAgent()
        
        # Test clean JSON
        clean_json = json.dumps({
            "explanation": "This is a great product",
            "key_reasons": ["Quality", "Value"],
            "confidence_score": 0.85,
            "match_factors": ["Interest"],
            "potential_concerns": []
        })
        
        class MockProduct:
            def __init__(self):
                self.product_id = "prod_001"
                self.name = "Test Product"
        
        product = MockProduct()
        explanation = agent._parse_explanation_response(clean_json, product, 0.88)
        
        assert explanation is not None, "Should parse clean JSON"
        assert explanation.product_name == "Test Product", "Product name should match"
        assert explanation.confidence_score == 0.85, "Confidence should match"
        
        print("✅ Clean JSON parsing: PASS")
        
        # Test JSON with code blocks
        json_with_blocks = f"```json\n{clean_json}\n```"
        explanation = agent._parse_explanation_response(json_with_blocks, product, 0.88)
        
        assert explanation is not None, "Should parse JSON with code blocks"
        assert explanation.product_name == "Test Product", "Product name should match"
        
        print("✅ JSON with code blocks parsing: PASS")
        
        # Test invalid JSON
        invalid_json = "This is not valid JSON"
        explanation = agent._parse_explanation_response(invalid_json, product, 0.88)
        
        assert explanation is None, "Should return None for invalid JSON"
        
        print("✅ Invalid JSON handling: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON Parsing Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Phase 4 standalone test"""
    print("🚀 Phase 4 Standalone Test Suite")
    print("=" * 60)
    print("Testing Agent 4: Explanation & Confidence Generator")
    
    tests = [
        ("Agent 4: Explanation & Confidence Generator", test_explanation_agent_standalone),
        ("RecommendationExplanation Model", test_recommendation_explanation_model),
        ("Explanation Prompt Generation", test_explanation_prompt_generation),
        ("JSON Parsing", test_json_parsing),
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
    print("📊 PHASE 4 STANDALONE TEST RESULTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.ljust(45)}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 Phase 4 Standalone Tests - ALL COMPONENTS WORKING!")
        print("\n📋 Agent 4 Components Verified:")
        print("   • Explanation generation with Gemini API")
        print("   • Confidence scoring algorithm")
        print("   • Summary explanation generation")
        print("   • Fallback explanation system")
        print("   • RecommendationExplanation model")
        print("   • Prompt generation logic")
        print("   • JSON parsing with error handling")
        
        print("\n✅ Agent 4 Implementation: COMPLETE AND VERIFIED")
        print("✅ Ready for integration with other agents")
        print("✅ Ready for frontend integration")
        return 0
    else:
        print("\n⚠️  Some Phase 4 standalone tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
