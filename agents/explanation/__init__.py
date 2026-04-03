"""
Explanation Agent Package
"""

# Import without initializing to avoid environment variable issues
from .agent import ExplanationAgent, RecommendationExplanation

# Don't initialize automatically
__all__ = ['ExplanationAgent', 'RecommendationExplanation']
