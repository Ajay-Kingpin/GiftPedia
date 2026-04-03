"""
Agent 1: Profile Analyzer
Extracts structured data from raw user input using Gemini Flash API
"""

import os
import json
import google.generativeai as genai
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator

class UserProfile(BaseModel):
    """Structured user profile extracted from natural language"""
    recipient_age: Optional[int] = Field(None, description="Recipient age in years")
    recipient_gender: str = Field("unknown", description="Recipient gender: male, female, non-binary, unknown")
    interests: list[str] = Field(default_factory=list, description="List of interests and hobbies")
    relationship: str = Field("other", description="Relationship: partner, friend, family, colleague, acquaintance, other")
    occasion: str = Field("other", description="Occasion: birthday, anniversary, wedding, festival, corporate, just_because, other")
    budget_inr: Optional[int] = Field(None, description="Budget in Indian Rupees")
    constraints: list[str] = Field(default_factory=list, description="Constraints or restrictions")

class ProfileAnalyzerAgent:
    """Extracts structured user profile from natural language input"""
    
    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.prompt_template = """
[System]
You are GiftPedia's Profile Analyzer. Your task is to extract structured information from user's gift request.

Extract the following information and output ONLY a valid JSON object:
{
  "recipient_age": integer or null,
  "recipient_gender": "male" | "female" | "non-binary" | "unknown",
  "interests": ["interest1", "interest2", ...],
  "relationship": "partner" | "friend" | "family" | "colleague" | "acquaintance" | "other",
  "occasion": "birthday" | "anniversary" | "wedding" | "festival" | "corporate" | "just_because" | "other",
  "budget_inr": integer or null,
  "constraints": ["constraint1", "constraint2", ...]
}

Rules:
- recipient_age: Extract number if mentioned, otherwise null
- recipient_gender: Infer from context, default to "unknown"
- interests: Extract hobbies, interests, preferences (lowercase)
- relationship: Map common terms to categories, default to "other"
- occasion: Map event types to categories, default to "other"
- budget_inr: Extract numeric value if mentioned, otherwise null
- constraints: Extract restrictions, allergies, preferences to avoid

Output ONLY of JSON object, no explanations or additional text.

[User Input]
{user_input}
"""

    def analyze(self, user_input: str) -> UserProfile:
        """
        Analyze user input and extract structured profile
        
        Args:
            user_input: Raw user input string
            
        Returns:
            UserProfile object with extracted information
        """
        return self.analyze_profile(user_input)
        try:
            # Generate prompt
            prompt = self.prompt_template.format(user_input=user_input)
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Clean response to extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            # Parse JSON
            profile_data = json.loads(json_text)
            
            # Validate with Pydantic
            profile = UserProfile(**profile_data)
            
            return profile
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response_text}")
            # Return default profile on error
            return UserProfile()
            
        except Exception as e:
            print(f"Profile analysis error: {e}")
            # Return default profile on error
            return UserProfile()

    def test_extraction(self, test_inputs: list[str]) -> list[Dict[str, Any]]:
        """
        Test the profile extraction with sample inputs
        
        Args:
            test_inputs: List of test input strings
            
        Returns:
            List of extraction results
        """
        results = []
        for input_text in test_inputs:
            try:
                profile = self.analyze(input_text)
                results.append({
                    "input": input_text,
                    "profile": profile.dict(),
                    "success": True
                })
            except Exception as e:
                results.append({
                    "input": input_text,
                    "error": str(e),
                    "success": False
                })
        return results

# Singleton instance
profile_analyzer = ProfileAnalyzerAgent()

if __name__ == "__main__":
    # Test the agent
    test_inputs = [
        "I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000",
        "Looking for anniversary gift for my wife who loves cooking and gardening, around ₹5000",
        "Need gift for male colleague who is into fitness, no budget constraints, just because",
        "Gift for teenage daughter who likes painting, birthday occasion, budget ₹1500, avoid plastic items"
    ]
    
    agent = ProfileAnalyzerAgent()
    results = agent.test_extraction(test_inputs)
    
    print("Profile Analyzer Test Results:")
    print("=" * 50)
    for result in results:
        print(f"Input: {result['input']}")
        if result['success']:
            print(f"Profile: {json.dumps(result['profile'], indent=2)}")
        else:
            print(f"Error: {result['error']}")
        print("-" * 50)
