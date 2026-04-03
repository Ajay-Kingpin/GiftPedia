import pytest
import json
import os
from unittest.mock import Mock, patch
import sys

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'agents', 'creative_idea'))

from agent import CreativeIdeaAgent, GiftConcept
from agents.profile_analyzer.agent import UserProfile

class TestCreativeIdeaAgent:
    """Test cases for Agent 2: Creative Idea Generator"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock the Gemini API key
        os.environ['GEMINI_API_KEY'] = 'test-api-key'
        
        # Create agent instance
        self.agent = CreativeIdeaAgent()
        
        # Mock response data
        self.mock_concepts_response = [
            {
                "concept": "Custom guitar pedal board with personalized engraving",
                "category": "Electronics",
                "reasoning": "Combines music interest with personal touch for memorable gift"
            },
            {
                "concept": "Vinyl record collection starter kit with classic albums",
                "category": "Music",
                "reasoning": "Perfect for music lover who appreciates physical media and nostalgia"
            }
        ]

    def test_gift_concept_creation(self):
        """Test GiftConcept model creation with valid data"""
        concept = GiftConcept(
            concept="Custom engraved watch",
            category="Fashion",
            reasoning="Personalized timepiece that matches recipient's style"
        )
        
        assert concept.concept == "Custom engraved watch"
        assert concept.category == "Fashion"
        assert concept.reasoning == "Personalized timepiece that matches recipient's style"

    @patch('agents.creative_idea.agent.genai')
    def test_generate_concepts_for_musician(self, mock_genai):
        """Test generating concepts for music enthusiast"""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps(self.mock_concepts_response)
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create test profile
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
        concepts = self.agent.generate_concepts(profile)
        
        # Assertions
        assert len(concepts) == 2
        assert concepts[0].category == "Electronics"
        assert "music" in concepts[0].reasoning.lower()
        assert concepts[1].category == "Music"

    @patch('agents.creative_idea.agent.genai')
    def test_generate_concepts_for_cooking_enthusiast(self, mock_genai):
        """Test generating concepts for cooking enthusiast"""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps([
            {
                "concept": "Smart herb garden with indoor growing system",
                "category": "Home & Garden",
                "reasoning": "Combines cooking interest with gardening passion perfectly"
            },
            {
                "concept": "Professional cooking class series with chef",
                "category": "Experience",
                "reasoning": "Educational experience that enhances cooking skills"
            }
        ])
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create test profile
        profile = UserProfile(
            recipient_age=35,
            recipient_gender="female",
            interests=["cooking", "gardening", "healthy_living"],
            relationship="partner",
            occasion="anniversary",
            budget_inr=5000,
            constraints=[]
        )
        
        # Generate concepts
        concepts = self.agent.generate_concepts(profile)
        
        # Assertions
        assert len(concepts) == 2
        assert any("garden" in concept.concept.lower() for concept in concepts)
        assert any("cooking" in concept.reasoning.lower() for concept in concepts)

    @patch('agents.creative_idea.agent.genai')
    def test_generate_with_budget_constraints(self, mock_genai):
        """Test generating concepts with budget constraints"""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps([
            {
                "concept": "High-quality yoga mat with carrying strap",
                "category": "Fitness",
                "reasoning": "Practical fitness gift within budget range"
            }
        ])
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create test profile with budget
        profile = UserProfile(
            recipient_age=30,
            recipient_gender="male",
            interests=["fitness", "yoga"],
            relationship="friend",
            occasion="birthday",
            budget_inr=1500,
            constraints=[]
        )
        
        # Generate concepts
        concepts = self.agent.generate_concepts(profile)
        
        # Assertions
        assert len(concepts) == 1
        assert concepts[0].category == "Fitness"

    @patch('agents.creative_idea.agent.genai')
    def test_json_parsing_with_code_blocks(self, mock_genai):
        """Test JSON parsing when response includes code blocks"""
        # Mock Gemini response with code blocks
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''```json
[
  {
    "concept": "Art subscription box with monthly supplies",
    "category": "Art & Crafts",
    "reasoning": "Ongoing creative experience for painting enthusiast"
  }
]
```'''
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create test profile
        profile = UserProfile(
            recipient_age=16,
            recipient_gender="female",
            interests=["painting", "art"],
            relationship="family",
            occasion="birthday",
            budget_inr=1500,
            constraints=[]
        )
        
        # Generate concepts
        concepts = self.agent.generate_concepts(profile)
        
        # Assertions
        assert len(concepts) == 1
        assert concepts[0].category == "Art & Crafts"
        assert "painting" in concepts[0].reasoning.lower()

    @patch('agents.creative_idea.agent.genai')
    def test_api_error_handling(self, mock_genai):
        """Test handling of API errors"""
        # Mock API error
        mock_genai.GenerativeModel.side_effect = Exception("API Error")
        
        # Create test profile
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="male",
            interests=["technology"],
            relationship="friend",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
        )
        
        # Generate concepts
        concepts = self.agent.generate_concepts(profile)
        
        # Should return default concept on error
        assert len(concepts) == 1
        assert concepts[0].concept == "Personalized gift based on interests"
        assert concepts[0].category == "Custom"

    @patch('agents.creative_idea.agent.genai')
    def test_json_parsing_error(self, mock_genai):
        """Test handling of JSON parsing errors"""
        # Mock invalid JSON response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create test profile
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="female",
            interests=["reading"],
            relationship="family",
            occasion="birthday",
            budget_inr=1000,
            constraints=[]
        )
        
        # Generate concepts
        concepts = self.agent.generate_concepts(profile)
        
        # Should return default concept on JSON error
        assert len(concepts) == 1
        assert concepts[0].category == "Custom"

    def test_missing_api_key(self):
        """Test initialization without API key"""
        # Remove API key from environment
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable not set"):
            CreativeIdeaAgent()

    def test_generation_with_multiple_profiles(self):
        """Test batch generation with multiple profiles"""
        test_profiles = [
            UserProfile(
                recipient_age=28,
                recipient_gender="male",
                interests=["music", "guitar"],
                relationship="family",
                occasion="birthday",
                budget_inr=2000,
                constraints=[]
            ),
            UserProfile(
                recipient_age=35,
                recipient_gender="female",
                interests=["cooking"],
                relationship="partner",
                occasion="anniversary",
                budget_inr=5000,
                constraints=[]
            )
        ]
        
        with patch('agents.creative_idea.agent.genai') as mock_genai:
            # Mock successful responses
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = json.dumps(self.mock_concepts_response)
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Test generation
            results = self.agent.test_generation(test_profiles)
            
            # Assertions
            assert len(results) == 2
            assert all(result['success'] for result in results)
            assert 'concepts' in results[0]
            assert len(results[0]['concepts']) == 2

    @patch('agents.creative_idea.agent.genai')
    def test_concept_validation(self, mock_genai):
        """Test validation of generated concepts"""
        # Mock Gemini response with invalid concept
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps([
            {
                # Missing required field 'concept'
                "category": "Electronics",
                "reasoning": "Good gift for tech enthusiast"
            }
        ])
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create test profile
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="male",
            interests=["technology"],
            relationship="friend",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
        )
        
        # Should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            self.agent.generate_concepts(profile)

if __name__ == "__main__":
    pytest.main([__file__])
