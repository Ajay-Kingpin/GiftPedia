#!/usr/bin/env python3
"""
Phase 2 Agent Tests
Test cases for Profile Analyzer and Creative Idea Generator agents
"""

import os
import sys
import json

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents', 'profile_analyzer'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'agents', 'creative_idea'))

# Set environment variable
os.environ['GEMINI_API_KEY'] = 'AIzaSyAoi-khzcttSvpXgVhuctAGubkBWvJFLSg'

def test_profile_analyzer():
    """Test Profile Analyzer with mock data"""
    print("🧪 Testing Profile Analyzer Agent...")
    
    try:
        from agent import ProfileAnalyzerAgent, UserProfile
        
        # Create agent
        agent = ProfileAnalyzerAgent()
        
        # Test data
        test_input = "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
        
        # Analyze
        profile = agent.analyze(test_input)
        
        print(f"✅ Input: {test_input}")
        print(f"✅ Extracted Profile:")
        print(f"   Age: {profile.recipient_age}")
        print(f"   Gender: {profile.recipient_gender}")
        print(f"   Interests: {profile.interests}")
        print(f"   Relationship: {profile.relationship}")
        print(f"   Occasion: {profile.occasion}")
        print(f"   Budget: ₹{profile.budget_inr}")
        print(f"   Constraints: {profile.constraints}")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile Analyzer Error: {e}")
        return False

def test_creative_idea_generator():
    """Test Creative Idea Generator with mock data"""
    print("\n🧪 Testing Creative Idea Generator Agent...")
    
    try:
        from agent import CreativeIdeaAgent, GiftConcept
        from agents.profile_analyzer.agent import UserProfile
        
        # Create agent
        agent = CreativeIdeaAgent()
        
        # Test profile
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar", "audio"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
        )
        
        # Generate concepts
        concepts = agent.generate_concepts(profile)
        
        print(f"✅ Input Profile: {profile.dict()}")
        print(f"✅ Generated Concepts:")
        for i, concept in enumerate(concepts, 1):
            print(f"   {i}. {concept.concept}")
            print(f"      Category: {concept.category}")
            print(f"      Reasoning: {concept.reasoning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Creative Idea Generator Error: {e}")
        return False

def test_agent_integration():
    """Test integration between Agent 1 and Agent 2"""
    print("\n🧪 Testing Agent Integration...")
    
    try:
        from agents.profile_analyzer.agent import profile_analyzer
        from agents.creative_idea.agent import creative_idea_agent
        
        # Test input
        user_input = "I need an anniversary gift for my wife who loves cooking and gardening, budget is ₹5000"
        
        print(f"✅ User Input: {user_input}")
        
        # Agent 1: Extract profile
        profile = profile_analyzer.analyze(user_input)
        print(f"✅ Agent 1 - Extracted Profile: {profile.dict()}")
        
        # Agent 2: Generate concepts
        concepts = creative_idea_agent.generate_concepts(profile)
        print(f"✅ Agent 2 - Generated {len(concepts)} concepts")
        
        for i, concept in enumerate(concepts, 1):
            print(f"   {i}. {concept.concept}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration Error: {e}")
        return False

def main():
    """Run all Phase 2 tests"""
    print("🚀 Phase 2 Agent Tests")
    print("=" * 50)
    
    tests = [
        ("Profile Analyzer", test_profile_analyzer),
        ("Creative Idea Generator", test_creative_idea_generator),
        ("Agent Integration", test_agent_integration),
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
    print("\n" + "=" * 50)
    print("📊 PHASE 2 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.ljust(25)}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Phase 2 agents are working correctly!")
        return 0
    else:
        print("⚠️  Some Phase 2 tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
