"""
Agent 4: Explanation & Confidence Generator
Generates explanations and confidence scores for gift recommendations
"""

import os
import json
import time
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from agents.profile_analyzer import UserProfile
from agents.creative_idea import GiftConcept
from agents.filter_rank import Product

class RecommendationExplanation(BaseModel):
    """Explanation for a gift recommendation"""
    product_id: str = Field(description="Product ID")
    product_name: str = Field(description="Product name")
    explanation: str = Field(description="Why this product is recommended (50-100 words)")
    key_reasons: List[str] = Field(description="3-5 key reasons for this recommendation")
    confidence_score: float = Field(description="Confidence score (0.0-1.0)")
    match_factors: List[str] = Field(description="Factors that contributed to this match")
    potential_concerns: List[str] = Field(default_factory=list, description="Potential concerns or considerations")

class ExplanationAgent:
    """Generates explanations and confidence scores for recommendations"""
    
    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_explanation(self, profile: UserProfile, concepts: List[GiftConcept], 
                            ranked_products: List[Dict[str, Any]]) -> List[RecommendationExplanation]:
        """
        Generate explanations for ranked products with comprehensive error handling
        
        Args:
            profile: User profile
            concepts: Creative concepts
            ranked_products: Ranked products from Agent 3
            
        Returns:
            List of recommendation explanations
        """
        explanations = []
        
        for item in ranked_products:
            # Handle different data structures from different filter rank agents
            if 'product' in item:
                product = item['product']
                similarity_score = item.get('similarity_score', 0.0)
                final_score = item.get('final_score', 0.0)
                product_id = item.get('product_id', product.get('product_id', 'unknown'))
                product_name = item.get('name', product.get('name', 'Unknown Product'))
            else:
                # Handle case where product details are directly in item
                product = item
                similarity_score = item.get('similarity_score', 0.0)
                final_score = item.get('final_score', 0.0)
                product_id = item.get('product_id', 'unknown')
                product_name = item.get('name', 'Unknown Product')
            
            # Create prompt for explanation
            prompt = self._create_explanation_prompt(profile, concepts, product, similarity_score, final_score)
            
            # Retry logic for API calls
            max_retries = 3
            retry_delay = 1.0  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Generate explanation
                    response = self.model.generate_content(prompt)
                    explanation_data = self._parse_explanation_response(response.text, product, final_score)
                    
                    if explanation_data:
                        # Validate explanation quality
                        if self._validate_explanation_quality(explanation_data):
                            explanations.append(explanation_data)
                        else:
                            # Use fallback if quality is poor
                            fallback = self._create_fallback_explanation(profile, product, final_score)
                            explanations.append(fallback)
                        break
                    else:
                        # Try to parse again with different approach
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                        else:
                            # Final fallback
                            fallback = self._create_fallback_explanation(profile, product, final_score)
                            explanations.append(fallback)
                            break
                        
                except Exception as e:
                    print(f"Explanation generation error (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        # Final fallback
                        print(f"Using fallback explanation for {product.name} after {max_retries} failed attempts")
                        fallback = self._create_fallback_explanation(profile, product, final_score)
                        explanations.append(fallback)
                        break
        
        return explanations
    
    def _validate_explanation_quality(self, explanation: RecommendationExplanation) -> bool:
        """Validate explanation quality before returning"""
        # Check explanation length
        if len(explanation.explanation) < 30 or len(explanation.explanation) > 500:
            return False
        
        # Check key reasons
        if len(explanation.key_reasons) < 2 or len(explanation.key_reasons) > 6:
            return False
        
        # Check confidence score
        if explanation.confidence_score < 0.1 or explanation.confidence_score > 1.0:
            return False
        
        # Check match factors
        if len(explanation.match_factors) < 1:
            return False
        
        # Check for meaningful content
        if not any(keyword in explanation.explanation.lower() for keyword in ['gift', 'perfect', 'great', 'ideal', 'excellent']):
            return False
        
        return True
    
    def _create_explanation_prompt(self, profile: UserProfile, concepts: List[GiftConcept], 
                                 product, similarity_score: float, final_score: float) -> str:
        """Create prompt for explanation generation"""
        
        # Extract product name safely
        product_name = getattr(product, 'name', 'Unknown Product')
        product_id = getattr(product, 'product_id', 'unknown')
        
        prompt = f"""
Generate a detailed explanation for why this gift recommendation is perfect for the user.

USER PROFILE:
- Age: {profile.recipient_age}
- Gender: {profile.recipient_gender}
- Interests: {', '.join(profile.interests)}
- Relationship: {profile.relationship}
- Occasion: {profile.occasion}
- Budget: ₹{profile.budget_inr}
- Constraints: {', '.join(profile.constraints) if profile.constraints else 'None'}

CREATIVE CONCEPTS:
{json.dumps([concept.dict() for concept in concepts[:2]], indent=2)}

RECOMMENDED PRODUCT:
- Name: {product.name}
- Category: {product.category}
- Price: ₹{product.price_inr}
- Brand: {product.brand}
- Tags: {', '.join(product.interest_tags)}

MATCH SCORES:
- Similarity Score: {similarity_score:.3f}
- Final Score: {final_score:.3f}

Generate a JSON response with the following structure:
{{
    "explanation": "Detailed explanation (50-100 words) explaining why this product matches the user's needs",
    "key_reasons": ["3-5 specific reasons why this is a good match"],
    "confidence_score": 0.85,
    "match_factors": ["factors that contributed to this recommendation"],
    "potential_concerns": ["any potential concerns or considerations"]
}}

Focus on:
1. How the product matches the recipient's interests
2. Why it's appropriate for the occasion and relationship
3. How it fits within the budget
4. Any unique features that make it special
5. How it addresses any constraints

Return ONLY the JSON response, no additional text.
"""
        return prompt
    
    def _parse_explanation_response(self, response_text: str, product: Product, final_score: float) -> Optional[RecommendationExplanation]:
        """Parse explanation response from Gemini"""
        try:
            # Extract JSON from response
            json_text = response_text.strip()
            
            # Remove code blocks if present
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.startswith('```'):
                json_text = json_text[3:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            
            json_text = json_text.strip()
            
            # Parse JSON
            data = json.loads(json_text)
            
            # Extract product name safely
        product_name = getattr(product, 'name', 'Unknown Product')
        product_id = getattr(product, 'product_id', 'unknown')
        
        # Create explanation object
        explanation = RecommendationExplanation(
            product_id=product_id,
            product_name=product_name,
            explanation=data.get('explanation', ''),
            key_reasons=data.get('key_reasons', []),
            confidence_score=self._calculate_confidence_score(final_score, data),
            match_factors=data.get('match_factors', []),
            potential_concerns=data.get('potential_concerns', [])
        )
            
            return explanation
            
        except Exception as e:
            print(f"JSON parsing error: {e}")
            return None
    
    def _calculate_confidence_score(self, final_score: float, explanation_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on multiple factors"""
        base_confidence = min(final_score, 1.0)
        
        # Adjust based on explanation quality
        explanation = explanation_data.get('explanation', '')
        key_reasons = explanation_data.get('key_reasons', [])
        
        quality_boost = 0.0
        
        # Good explanation length (50-100 words ~ 250-500 characters)
        explanation_length = len(explanation)
        if 250 <= explanation_length <= 500:
            quality_boost += 0.05
        elif 150 <= explanation_length <= 600:
            quality_boost += 0.03
        
        # Sufficient key reasons
        if len(key_reasons) >= 3:
            quality_boost += 0.05
        elif len(key_reasons) >= 2:
            quality_boost += 0.02
        
        # Specific keywords indicating confidence
        confidence_keywords = ['perfect', 'ideal', 'excellent', 'great match', 'highly recommended', 'perfectly suited']
        if any(keyword in explanation.lower() for keyword in confidence_keywords):
            quality_boost += 0.05
        
        # Quality indicators
        quality_keywords = ['quality', 'craftsmanship', 'durable', 'premium', 'high-quality']
        if any(keyword in explanation.lower() for keyword in quality_keywords):
            quality_boost += 0.03
        
        # Practical value indicators
        practical_keywords = ['practical', 'useful', 'functional', 'versatile']
        if any(keyword in explanation.lower() for keyword in practical_keywords):
            quality_boost += 0.02
        
        final_confidence = min(base_confidence + quality_boost, 1.0)
        return round(final_confidence, 2)
    
    def _create_fallback_explanation(self, profile: UserProfile, product: Product, final_score: float) -> RecommendationExplanation:
        """Create fallback explanation when API fails"""
        # Extract product name safely
        product_name = getattr(product, 'name', 'Unknown Product')
        product_id = getattr(product, 'product_id', 'unknown')
        
        # Generate basic explanation with more detail
        explanation_parts = []
        
        # Product description
        explanation_parts.append(f"This {product_name} is an excellent choice for {profile.relationship}'s {profile.occasion}")
        
        # Interest alignment
        if profile.interests:
            interests_str = ', '.join(profile.interests[:2])
            explanation_parts.append(f"It perfectly matches their interests in {interests_str}")
        
        # Budget compatibility
        explanation_parts.append(f"and fits well within your budget of ₹{profile.budget_inr}")
        
        # Quality and value
        explanation_parts.append(f"The {getattr(product, 'brand', 'premium')} quality and thoughtful features make it a meaningful gift")
        
        # Occasion appropriateness
        explanation_parts.append(f"that's perfectly suited for this {profile.occasion} celebration")
        
        explanation = " ".join(explanation_parts) + "."
        
        # Generate key reasons with more variety
        key_reasons = [
            f"Perfectly matches {profile.interests[0] if profile.interests else 'their'} interests",
            f"Ideal for {profile.occasion} occasions",
            f"Excellent value at ₹{product.price_inr}",
            f"High-quality {product.category.lower()} product",
            f"Thoughtful gift for {profile.relationship}"
        ]
        
        # Generate match factors
        match_factors = [
            "Interest alignment",
            "Budget compatibility", 
            "Occasion appropriateness",
            "Product quality",
            "Brand reputation"
        ]
        
        # Add potential concerns if applicable
        potential_concerns = []
        if product.price_inr > profile.budget_inr * 0.8:
            potential_concerns.append("Near upper budget limit")
        if len(profile.constraints) > 0:
            potential_concerns.append("Review against specific constraints")
        
        # Calculate confidence (slightly lower for fallback)
        confidence = min(final_score * 0.85, 0.80)  # Conservative fallback confidence
        
        return RecommendationExplanation(
            product_id=product.product_id,
            product_name=product.name,
            explanation=explanation,
            key_reasons=key_reasons,
            confidence_score=confidence,
            match_factors=match_factors,
            potential_concerns=potential_concerns
        )
    
    def generate_summary_explanation(self, explanations: List[RecommendationExplanation], 
                                   profile: UserProfile) -> str:
        """
        Generate a summary explanation for all recommendations
        
        Args:
            explanations: List of recommendation explanations
            profile: User profile
            
        Returns:
            Summary explanation
        """
        if not explanations:
            return "No recommendations available at this time."
        
        try:
            # Create comprehensive prompt for summary
            prompt = f"""
Generate a warm, personalized summary for these gift recommendations.

USER PROFILE:
- Age: {profile.recipient_age}
- Gender: {profile.recipient_gender}
- Interests: {', '.join(profile.interests)}
- Relationship: {profile.relationship}
- Occasion: {profile.occasion}
- Budget: ₹{profile.budget_inr}

RECOMMENDATIONS:
{json.dumps([exp.dict() for exp in explanations[:3]], indent=2)}

Generate a warm, conversational summary (120-180 words) that:
1. Acknowledges the special relationship and occasion
2. Highlights how the recommendations match their interests
3. Emphasizes the thoughtful consideration behind each choice
4. Mentions the budget-friendly nature of the selections
5. Conveys confidence in these being perfect gifts

Use a friendly, encouraging tone. Focus on making the gift-giver feel confident about their choices.
Avoid generic language - make it feel personal and specific to this recipient.
"""
            
            # Generate summary
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            # Clean up response
            if summary.startswith('```'):
                summary = summary[3:]
            if summary.endswith('```'):
                summary = summary[:-3]
            
            summary = summary.strip()
            
            # Validate summary quality
            if len(summary) < 80 or len(summary) > 300:
                # Fallback to enhanced default summary
                return self._create_enhanced_fallback_summary(explanations, profile)
            
            return summary
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            # Enhanced fallback summary
            return self._create_enhanced_fallback_summary(explanations, profile)
    
    def _create_enhanced_fallback_summary(self, explanations: List[RecommendationExplanation], 
                                         profile: UserProfile) -> str:
        """Create enhanced fallback summary when API fails"""
        interests = ', '.join(profile.interests[:2])
        relationship = profile.relationship
        occasion = profile.occasion
        budget = profile.budget_inr
        
        summary_parts = []
        
        # Opening with personal touch
        summary_parts.append(f"Finding the perfect {occasion} gift for your {relationship} is important, and we've found some wonderful options that truly celebrate their interests.")
        
        # Interest alignment
        summary_parts.append(f"Each recommendation has been carefully chosen to match their passion for {interests}, ensuring the gift will be both meaningful and useful.")
        
        # Quality and value
        summary_parts.append(f"We've focused on high-quality items that offer excellent value within your ₹{budget} budget, so you can give with confidence.")
        
        # Personal touch and confidence
        summary_parts.append(f"These thoughtful selections show you understand what makes them special, making this {occasion} truly memorable.")
        
        # Closing
        summary_parts.append(f"Each gift comes with our confidence that it will bring joy and appreciation to your {relationship}.")
        
        return " ".join(summary_parts)

# Singleton instance
explanation_agent = ExplanationAgent()

if __name__ == "__main__":
    # Test the agent
    from agents.profile_analyzer import UserProfile
    from agents.creative_idea import GiftConcept
    from agents.filter_rank import Product
    
    # Mock profile
    profile = UserProfile(
        recipient_age=28,
        recipient_gender="male",
        interests=["music", "guitar"],
        relationship="family",
        occasion="birthday",
        budget_inr=2000,
        constraints=[]
    )
    
    # Mock concepts
    concepts = [
        GiftConcept(
            concept="Custom guitar accessories",
            category="Music",
            reasoning="Perfect for music enthusiast"
        )
    ]
    
    # Mock ranked products
    mock_product = Product(
        product_id="prod_001",
        name="Fender Guitar Strap",
        category="Music & Instruments",
        price_inr=1899.0,
        brand="Fender",
        interest_tags=["music", "guitar"]
    )
    
    ranked_products = [
        {
            'product': mock_product,
            'similarity_score': 0.95,
            'final_score': 1.15
        }
    ]
    
    # Test explanation generation
    agent = ExplanationAgent()
    explanations = agent.generate_explanation(profile, concepts, ranked_products)
    
    print("Explanation Agent Test Results:")
    print("=" * 50)
    
    for exp in explanations:
        print(f"Product: {exp.product_name}")
        print(f"Explanation: {exp.explanation}")
        print(f"Confidence: {exp.confidence_score}")
        print(f"Key Reasons: {exp.key_reasons}")
        print(f"Match Factors: {exp.match_factors}")
        print("-" * 30)
