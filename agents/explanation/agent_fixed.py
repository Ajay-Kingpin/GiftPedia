"""
Agent 4: Explanation & Confidence Generator (Fixed Version)
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
                        print(f"Using fallback explanation for {product_name} after {max_retries} failed attempts")
                        fallback = self._create_fallback_explanation(profile, product, final_score)
                        explanations.append(fallback)
                        break
        
        return explanations
    
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

CREATIVE CONCEPTS:
{chr(10).join([f"- {concept.concept}: {concept.reasoning}" for concept in concepts])}

PRODUCT RECOMMENDATION:
- Product ID: {product_id}
- Name: {product_name}
- Similarity Score: {similarity_score:.3f}
- Final Score: {final_score:.3f}

TASK:
Generate a compelling explanation (50-100 words) for why this {product_name} is an excellent gift choice.

Focus on:
1. How it matches the recipient's interests and personality
2. Why it's perfect for the {profile.occasion} occasion
3. The value and quality it offers
4. Any special features that make it thoughtful

Return a JSON object with:
- explanation: The main recommendation text
- key_reasons: 3-5 bullet points
- confidence_score: 0.0-1.0
- match_factors: 2-3 factors
- potential_concerns: Any considerations

Make the explanation sound natural, confident, and helpful.
"""
        
        return prompt
    
    def _parse_explanation_response(self, response_text: str, product, final_score: float) -> Optional[RecommendationExplanation]:
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
            f"Excellent value within budget of ₹{profile.budget_inr}",
            f"Premium {getattr(product, 'brand', 'quality')} quality and craftsmanship"
        ]
        
        # Calculate confidence score for fallback
        base_confidence = min(final_score, 1.0)
        fallback_confidence = min(base_confidence + 0.2, 1.0)  # Slightly lower for fallback
        
        return RecommendationExplanation(
            product_id=product_id,
            product_name=product_name,
            explanation=explanation,
            key_reasons=key_reasons,
            confidence_score=fallback_confidence,
            match_factors=["Interest alignment", "Budget fit", "Quality value"],
            potential_concerns=["Consider personal preferences"]
        )

# Global agent instance
explanation_agent = ExplanationAgent()
