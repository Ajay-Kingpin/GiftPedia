import pytest
import os
from unittest.mock import Mock, patch
import sys

# Add the agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'agents', 'explanation'))

from agent import ExplanationAgent, RecommendationExplanation

class TestExplanationAgent:
    """Test cases for Agent 4: Explanation & Confidence Generator"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Mock environment variables
        os.environ['GEMINI_API_KEY'] = 'test-gemini-key'
        
        # Create agent instance
        self.agent = ExplanationAgent()

    def test_recommendation_explanation_creation(self):
        """Test RecommendationExplanation model creation"""
        explanation = RecommendationExplanation(
            product_id="prod_001",
            product_name="Fender Guitar Strap",
            explanation="Perfect gift for music enthusiasts who love guitar accessories",
            key_reasons=["Matches music interest", "High quality", "Good value"],
            confidence_score=0.85,
            match_factors=["Interest alignment", "Budget compatibility"],
            potential_concerns=["May need additional accessories"]
        )
        
        assert explanation.product_id == "prod_001"
        assert explanation.product_name == "Fender Guitar Strap"
        assert explanation.confidence_score == 0.85
        assert len(explanation.key_reasons) == 3

    @patch('agent.genai')
    def test_generate_explanation_success(self, mock_genai):
        """Test successful explanation generation"""
        # Mock Gemini response
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
        
        # Mock data
        from agents.profile_analyzer import UserProfile
        from agents.creative_idea import GiftConcept
        from agents.filter_rank import Product
        
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
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
            interest_tags=["music", "guitar"]
        )
        
        ranked_products = [
            {
                'product': product,
                'similarity_score': 0.95,
                'final_score': 1.15
            }
        ]
        
        # Generate explanations
        explanations = self.agent.generate_explanation(profile, concepts, ranked_products)
        
        # Assertions
        assert len(explanations) == 1
        explanation = explanations[0]
        assert explanation.product_id == "prod_001"
        assert explanation.product_name == "Fender Guitar Strap"
        assert explanation.confidence_score == 0.85
        assert len(explanation.key_reasons) == 3

    @patch('agent.genai')
    def test_generate_explanation_with_code_blocks(self, mock_genai):
        """Test explanation generation with code blocks in response"""
        # Mock Gemini response with code blocks
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = '''```json
{
    "explanation": "This guitar strap is ideal for musicians who value comfort and style.",
    "key_reasons": ["Comfortable design", "Stylish appearance", "Durable materials"],
    "confidence_score": 0.90,
    "match_factors": ["Interest match", "Quality brand"],
    "potential_concerns": []
}
```'''
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Mock data
        from agents.profile_analyzer import UserProfile
        from agents.creative_idea import GiftConcept
        from agents.filter_rank import Product
        
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="female",
            interests=["music"],
            relationship="friend",
            occasion="birthday",
            budget_inr=1500,
            constraints=[]
        )
        
        concepts = [GiftConcept(concept="Music accessories", category="Music", reasoning="Good for music lovers")]
        
        product = Product(
            product_id="prod_002",
            name="Leather Guitar Strap",
            category="Music & Instruments",
            price_inr=1299.0,
            brand="Generic",
            interest_tags=["music"]
        )
        
        ranked_products = [{'product': product, 'similarity_score': 0.88, 'final_score': 1.05}]
        
        # Generate explanations
        explanations = self.agent.generate_explanation(profile, concepts, ranked_products)
        
        # Assertions
        assert len(explanations) == 1
        explanation = explanations[0]
        assert explanation.confidence_score == 0.90
        assert len(explanation.key_reasons) == 3

    @patch('agent.genai')
    def test_generate_explanation_api_error(self, mock_genai):
        """Test explanation generation with API error"""
        # Mock API error
        mock_genai.GenerativeModel.side_effect = Exception("API Error")
        
        # Mock data
        from agents.profile_analyzer import UserProfile
        from agents.creative_idea import GiftConcept
        from agents.filter_rank import Product
        
        profile = UserProfile(
            recipient_age=30,
            recipient_gender="male",
            interests=["fitness"],
            relationship="colleague",
            occasion="just_because",
            budget_inr=1000,
            constraints=[]
        )
        
        concepts = [GiftConcept(concept="Fitness gear", category="Fitness", reasoning="Good for health")]
        
        product = Product(
            product_id="prod_003",
            name="Yoga Mat",
            category="Fitness",
            price_inr=899.0,
            brand="FitnessBrand",
            interest_tags=["fitness", "yoga"]
        )
        
        ranked_products = [{'product': product, 'similarity_score': 0.75, 'final_score': 0.85}]
        
        # Generate explanations (should use fallback)
        explanations = self.agent.generate_explanation(profile, concepts, ranked_products)
        
        # Assertions
        assert len(explanations) == 1
        explanation = explanations[0]
        assert explanation.product_id == "prod_003"
        assert explanation.product_name == "Yoga Mat"
        assert explanation.confidence_score < 1.0  # Fallback should have lower confidence

    def test_calculate_confidence_score(self):
        """Test confidence score calculation"""
        explanation_data = {
            "explanation": "This is a perfect match with great features and excellent quality.",
            "key_reasons": ["Perfect match", "Great features", "Excellent quality", "Highly recommended"]
        }
        
        # Test high score
        confidence = self.agent._calculate_confidence_score(0.95, explanation_data)
        assert confidence >= 0.85, "High score should result in high confidence"
        
        # Test low score
        confidence = self.agent._calculate_confidence_score(0.60, explanation_data)
        assert confidence <= 0.70, "Low score should result in lower confidence"

    def test_create_fallback_explanation(self):
        """Test fallback explanation creation"""
        from agents.profile_analyzer import UserProfile
        from agents.filter_rank import Product
        
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="female",
            interests=["reading", "books"],
            relationship="partner",
            occasion="anniversary",
            budget_inr=2000,
            constraints=[]
        )
        
        product = Product(
            product_id="prod_004",
            name="Classic Book Collection",
            category="Books",
            price_inr=1899.0,
            brand="LiteraryClassics",
            interest_tags=["reading", "books"]
        )
        
        # Create fallback explanation
        explanation = self.agent._create_fallback_explanation(profile, product, 0.88)
        
        # Assertions
        assert explanation.product_id == "prod_004"
        assert explanation.product_name == "Classic Book Collection"
        assert len(explanation.key_reasons) == 4
        assert len(explanation.match_factors) == 4
        assert explanation.confidence_score < 0.88  # Should be slightly lower

    @patch('agent.genai')
    def test_generate_summary_explanation(self, mock_genai):
        """Test summary explanation generation"""
        # Mock Gemini response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Based on the recipient's interests in music and guitar, we've selected high-quality accessories that are perfect for their birthday. These recommendations offer excellent value and functionality."
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Mock explanations
        explanations = [
            RecommendationExplanation(
                product_id="prod_001",
                product_name="Fender Guitar Strap",
                explanation="Perfect for guitar enthusiasts",
                key_reasons=["Quality", "Value"],
                confidence_score=0.85,
                match_factors=["Interest"],
                potential_concerns=[]
            )
        ]
        
        from agents.profile_analyzer import UserProfile
        profile = UserProfile(
            recipient_age=28,
            recipient_gender="male",
            interests=["music", "guitar"],
            relationship="family",
            occasion="birthday",
            budget_inr=2000,
            constraints=[]
        )
        
        # Generate summary
        summary = self.agent.generate_summary_explanation(explanations, profile)
        
        # Assertions
        assert len(summary) > 50, "Summary should be substantial"
        assert "music" in summary, "Summary should mention interests"
        assert "birthday" in summary, "Summary should mention occasion"

    def test_generate_summary_explanation_fallback(self, mock_genai):
        """Test summary explanation generation with fallback"""
        # Mock API error
        mock_genai.GenerativeModel.side_effect = Exception("API Error")
        
        # Mock explanations
        explanations = [
            RecommendationExplanation(
                product_id="prod_001",
                product_name="Test Product",
                explanation="Test explanation",
                key_reasons=["Test reason"],
                confidence_score=0.80,
                match_factors=["Test factor"],
                potential_concerns=[]
            )
        ]
        
        from agents.profile_analyzer import UserProfile
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="female",
            interests=["cooking"],
            relationship="friend",
            occasion="birthday",
            budget_inr=1500,
            constraints=[]
        )
        
        # Generate summary (should use fallback)
        summary = self.agent.generate_summary_explanation(explanations, profile)
        
        # Assertions
        assert len(summary) > 50, "Fallback summary should be substantial"
        assert "cooking" in summary, "Fallback summary should mention interests"
        assert "birthday" in summary, "Fallback summary should mention occasion"

    def test_missing_api_key(self):
        """Test initialization without API key"""
        # Remove API key from environment
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable not set"):
            ExplanationAgent()

    def test_json_parsing_error(self, mock_genai):
        """Test JSON parsing error handling"""
        # Mock invalid JSON response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Mock data
        from agents.profile_analyzer import UserProfile
        from agents.creative_idea import GiftConcept
        from agents.filter_rank import Product
        
        profile = UserProfile(
            recipient_age=30,
            recipient_gender="male",
            interests=["technology"],
            relationship="friend",
            occasion="birthday",
            budget_inr=1000,
            constraints=[]
        )
        
        concepts = [GiftConcept(concept="Tech gadget", category="Electronics", reasoning="Modern gift")]
        
        product = Product(
            product_id="prod_005",
            name="Smart Watch",
            category="Electronics",
            price_inr=999.0,
            brand="TechBrand",
            interest_tags=["technology"]
        )
        
        ranked_products = [{'product': product, 'similarity_score': 0.80, 'final_score': 0.90}]
        
        # Generate explanations (should use fallback)
        explanations = self.agent.generate_explanation(profile, concepts, ranked_products)
        
        # Should return fallback explanation
        assert len(explanations) == 1
        assert explanations[0].product_id == "prod_005"

    def test_empty_explanations_summary(self):
        """Test summary generation with empty explanations"""
        from agents.profile_analyzer import UserProfile
        
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="female",
            interests=["art"],
            relationship="family",
            occasion="birthday",
            budget_inr=1500,
            constraints=[]
        )
        
        # Generate summary with empty explanations
        summary = self.agent.generate_summary_explanation([], profile)
        
        # Should return default message
        assert summary == "No recommendations available at this time."

if __name__ == "__main__":
    pytest.main([__file__])
