"""
Profile Analyzer Agent Package
"""

# Import without initializing to avoid environment variable issues
from .agent import ProfileAnalyzerAgent, UserProfile

# Don't initialize automatically
__all__ = ['ProfileAnalyzerAgent', 'UserProfile']
