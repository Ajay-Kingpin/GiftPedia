import pytest
import json
import os
from unittest.mock import Mock, patch
import sys

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'agents', 'profile_analyzer'))

from agent import ProfileAnalyzerAgent, UserProfile

class TestProfileAnalyzerAgent:
    """Test cases for Agent 1: Profile Analyzer"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock the Gemini API key
        os.environ['GEMINI_API_KEY'] = 'test-api-key'
        
        # Create agent instance
        self.agent = ProfileAnalyzerAgent()
        
        # Mock response data
        self.mock_profile_response = {
            "recipient_age": 28,
            "recipient_gender": "male",
            "interests": ["music", "guitar", "musician"],
            "relationship": "family",
            "occasion": "birthday",
            "budget_inr": 2000,
            "constraints": []
        }

    def test_user_profile_creation(self):
        """Test UserProfile model creation with valid data"""
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="female",
            interests=["reading", "cooking"],
            relationship="friend",
            occasion="birthday",
            budget_inr=1500,
            constraints=["no plastic"]
        )
        
        assert profile.recipient_age == 25
        assert profile.recipient_gender == "female"
        assert profile.interests == ["reading", "cooking"]
        assert profile.relationship == "friend"
        assert profile.occasion == "birthday"
        assert profile.budget_inr == 1500
        assert profile.constraints == ["no plastic"]

    def test_user_profile_defaults(self):
        """Test UserProfile model with default values"""
        profile = UserProfile()
        
        assert profile.recipient_age is None
        assert profile.recipient_gender == "unknown"
        assert profile.interests == []
        assert profile.relationship == "other"
        assert profile.occasion == "other"
        assert profile.budget_inr is None
        assert profile.constraints == []

    @patch('agents.profile_analyzer.agent.genai')
    def test_analyze_brother_birthday_gift(self, mock_genai):
        """Test analyzing birthday gift for brother"""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps(self.mock_profile_response)
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test input
        user_input = "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
        
        # Analyze
        profile = self.agent.analyze(user_input)
        
        # Assertions
        assert profile.recipient_age == 28
        assert profile.recipient_gender == "male"
        assert "music" in profile.interests
        assert profile.relationship == "family"
        assert profile.occasion == "birthday"
        assert profile.budget_inr == 2000

    @patch('agents.profile_analyzer.agent.genai')
    def test_analyze_wife_anniversary_gift(self, mock_genai):
        """Test analyzing anniversary gift for wife"""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "recipient_age": None,
            "recipient_gender": "female",
            "interests": ["cooking", "gardening"],
            "relationship": "partner",
            "occasion": "anniversary",
            "budget_inr": 5000,
            "constraints": []
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test input
        user_input = "Looking for anniversary gift for my wife who loves cooking and gardening, around ₹5000"
        
        # Analyze
        profile = self.agent.analyze(user_input)
        
        # Assertions
        assert profile.recipient_age is None
        assert profile.recipient_gender == "female"
        assert "cooking" in profile.interests
        assert "gardening" in profile.interests
        assert profile.relationship == "partner"
        assert profile.occasion == "anniversary"
        assert profile.budget_inr == 5000

    @patch('agents.profile_analyzer.agent.genai')
    def test_analyze_colleague_just_because(self, mock_genai):
        """Test analyzing gift for colleague with no budget"""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "recipient_age": None,
            "recipient_gender": "male",
            "interests": ["fitness"],
            "relationship": "colleague",
            "occasion": "just_because",
            "budget_inr": None,
            "constraints": []
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test input
        user_input = "Need gift for male colleague who is into fitness, no budget constraints, just because"
        
        # Analyze
        profile = self.agent.analyze(user_input)
        
        # Assertions
        assert profile.recipient_age is None
        assert profile.recipient_gender == "male"
        assert "fitness" in profile.interests
        assert profile.relationship == "colleague"
        assert profile.occasion == "just_because"
        assert profile.budget_inr is None

    @patch('agents.profile_analyzer.agent.genai')
    def test_analyze_with_constraints(self, mock_genai):
        """Test analyzing gift with constraints"""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = json.dumps({
            "recipient_age": 16,
            "recipient_gender": "female",
            "interests": ["painting", "art"],
            "relationship": "family",
            "occasion": "birthday",
            "budget_inr": 1500,
            "constraints": ["no plastic", "eco-friendly"]
        })
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test input
        user_input = "Gift for teenage daughter who likes painting, birthday occasion, budget ₹1500, avoid plastic items"
        
        # Analyze
        profile = self.agent.analyze(user_input)
        
        # Assertions
        assert profile.recipient_age == 16
        assert profile.recipient_gender == "female"
        assert "painting" in profile.interests
        assert profile.constraints == ["no plastic", "eco-friendly"]

    @patch('agents.profile_analyzer.agent.genai')
    def test_json_parsing_with_code_blocks(self, mock_genai):
        """Test JSON parsing when response includes code blocks"""
        # Mock Gemini response with code blocks
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''```json
{
  "recipient_age": 30,
  "recipient_gender": "male",
  "interests": ["technology", "gaming"],
  "relationship": "friend",
  "occasion": "birthday",
  "budget_inr": 3000,
  "constraints": []
}
```'''
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test input
        user_input = "Gift for 30-year-old male friend who loves technology and gaming, budget ₹3000"
        
        # Analyze
        profile = self.agent.analyze(user_input)
        
        # Assertions
        assert profile.recipient_age == 30
        assert profile.recipient_gender == "male"
        assert "technology" in profile.interests
        assert "gaming" in profile.interests

    @patch('agents.profile_analyzer.agent.genai')
    def test_api_error_handling(self, mock_genai):
        """Test handling of API errors"""
        # Mock API error
        mock_genai.GenerativeModel.side_effect = Exception("API Error")
        
        # Test input
        user_input = "Test input"
        
        # Analyze
        profile = self.agent.analyze(user_input)
        
        # Should return default profile on error
        assert profile.recipient_age is None
        assert profile.recipient_gender == "unknown"
        assert profile.interests == []

    @patch('agents.profile_analyzer.agent.genai')
    def test_json_parsing_error(self, mock_genai):
        """Test handling of JSON parsing errors"""
        # Mock invalid JSON response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Test input
        user_input = "Test input"
        
        # Analyze
        profile = self.agent.analyze(user_input)
        
        # Should return default profile on JSON error
        assert profile.recipient_age is None
        assert profile.recipient_gender == "unknown"
        assert profile.interests == []

    def test_missing_api_key(self):
        """Test initialization without API key"""
        # Remove API key from environment
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable not set"):
            ProfileAnalyzerAgent()

    def test_extraction_with_multiple_inputs(self):
        """Test batch extraction with multiple inputs"""
        test_inputs = [
            "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000",
            "Looking for anniversary gift for my wife who loves cooking and gardening, around ₹5000"
        ]
        
        with patch('agents.profile_analyzer.agent.genai') as mock_genai:
            # Mock successful responses
            mock_model = Mock()
            mock_response = Mock()
            mock_response.text = json.dumps(self.mock_profile_response)
            mock_model.generate_content.return_value = mock_response
            mock_genai.GenerativeModel.return_value = mock_model
            
            # Test extraction
            results = self.agent.test_extraction(test_inputs)
            
            # Assertions
            assert len(results) == 2
            assert all(result['success'] for result in results)
            assert 'input' in results[0]
            assert 'profile' in results[0]

if __name__ == "__main__":
    pytest.main([__file__])
