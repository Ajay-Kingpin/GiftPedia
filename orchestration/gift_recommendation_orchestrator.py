"""
Gift Recommendation Orchestrator
Coordinates all agents for end-to-end gift recommendation workflow
"""

import os
import sys
import time
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents import (
    ProfileAnalyzerAgent, UserProfile,
    CreativeIdeaAgent, GiftConcept,
    FilterRankAgent, Product,
    ExplanationAgent, RecommendationExplanation
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RecommendationRequest:
    """Request for gift recommendations"""
    user_input: str
    session_id: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None
    max_recommendations: int = 5

@dataclass
class RecommendationResponse:
    """Response containing gift recommendations"""
    profile: UserProfile
    concepts: List[GiftConcept]
    recommendations: List[Dict[str, Any]]
    explanations: List[RecommendationExplanation]
    summary: str
    processing_time: float
    session_id: str
    timestamp: datetime
    metadata: Dict[str, Any]

class GiftRecommendationOrchestrator:
    """Main orchestrator for gift recommendation workflow"""
    
    def __init__(self):
        """Initialize all agents"""
        self.profile_analyzer = ProfileAnalyzerAgent()
        self.creative_agent = CreativeIdeaAgent()
        self.filter_rank_agent = FilterRankAgent()
        self.explanation_agent = ExplanationAgent()
        
        # Performance tracking
        self.performance_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0,
            'agent_performance': {
                'profile_analyzer': {'avg_time': 0.0, 'success_rate': 1.0},
                'creative_idea': {'avg_time': 0.0, 'success_rate': 1.0},
                'filter_rank': {'avg_time': 0.0, 'success_rate': 1.0},
                'explanation': {'avg_time': 0.0, 'success_rate': 1.0}
            }
        }
        
        logger.info("Gift Recommendation Orchestrator initialized")
    
    def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Process gift recommendation request through complete workflow
        
        Args:
            request: Recommendation request with user input
            
        Returns:
            RecommendationResponse with all results
        """
        start_time = time.time()
        session_id = request.session_id or f"session_{int(time.time())}"
        
        try:
            logger.info(f"Processing request for session: {session_id}")
            
            # Agent 1: Profile Analysis
            logger.info("Step 1: Analyzing user profile...")
            profile_start = time.time()
            profile = self.profile_analyzer.analyze(request.user_input)
            profile_time = time.time() - profile_start
            self._update_agent_performance('profile_analyzer', profile_time, True)
            logger.info(f"Profile analyzed in {profile_time:.2f}s")
            
            # Agent 2: Creative Idea Generation
            logger.info("Step 2: Generating creative concepts...")
            creative_start = time.time()
            concepts = self.creative_agent.generate_concepts(profile)
            creative_time = time.time() - creative_start
            self._update_agent_performance('creative_idea', creative_time, True)
            logger.info(f"Generated {len(concepts)} concepts in {creative_time:.2f}s")
            
            # Agent 3: Filter & Rank Products
            logger.info("Step 3: Filtering and ranking products...")
            filter_start = time.time()
            ranked_products = self.filter_rank_agent.filter_and_rank(profile, concepts)
            filter_time = time.time() - filter_start
            self._update_agent_performance('filter_rank', filter_time, True)
            logger.info(f"Ranked {len(ranked_products)} products in {filter_time:.2f}s")
            
            # Agent 4: Generate Explanations
            logger.info("Step 4: Generating explanations...")
            explanation_start = time.time()
            explanations = self.explanation_agent.generate_explanation(profile, concepts, ranked_products)
            explanation_time = time.time() - explanation_start
            self._update_agent_performance('explanation', explanation_time, True)
            logger.info(f"Generated {len(explanations)} explanations in {explanation_time:.2f}s")
            
            # Generate summary
            summary = self.explanation_agent.generate_summary_explanation(explanations, profile)
            
            # Prepare recommendations for frontend
            recommendations = self._prepare_recommendations(ranked_products, explanations)
            
            total_time = time.time() - start_time
            
            # Update performance metrics
            self.performance_metrics['total_requests'] += 1
            self.performance_metrics['successful_requests'] += 1
            self._update_average_processing_time(total_time)
            
            # Create response
            response = RecommendationResponse(
                profile=profile,
                concepts=concepts,
                recommendations=recommendations,
                explanations=explanations,
                summary=summary,
                processing_time=total_time,
                session_id=session_id,
                timestamp=datetime.now(),
                metadata={
                    'agent_times': {
                        'profile_analyzer': profile_time,
                        'creative_idea': creative_time,
                        'filter_rank': filter_time,
                        'explanation': explanation_time
                    },
                    'input_length': len(request.user_input),
                    'max_recommendations': request.max_recommendations
                }
            )
            
            logger.info(f"Successfully processed request in {total_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self.performance_metrics['total_requests'] += 1
            self.performance_metrics['failed_requests'] += 1
            
            # Create error response
            return self._create_error_response(request, str(e), session_id, start_time)
    
    def _prepare_recommendations(self, ranked_products: List[Dict[str, Any]], 
                               explanations: List[RecommendationExplanation]) -> List[Dict[str, Any]]:
        """Prepare recommendations for frontend consumption"""
        recommendations = []
        
        for i, ranked_product in enumerate(ranked_products):
            product = ranked_product['product']
            explanation = explanations[i] if i < len(explanations) else None
            
            recommendation = {
                'product_id': product.product_id,
                'name': product.name,
                'category': product.category,
                'price_inr': product.price_inr,
                'brand': product.brand,
                'image_url': f"https://picsum.photos/seed/{product.product_id}/400/300.jpg",
                'affiliate_link': f"https://example.com/affiliate/{product.product_id}",
                'similarity_score': ranked_product.get('similarity_score', 0.0),
                'final_score': ranked_product.get('final_score', 0.0),
                'explanation': explanation.dict() if explanation else None,
                'interest_tags': product.interest_tags,
                'occasion_tags': product.occasion_tags,
                'relationship_tags': product.relationship_tags
            }
            
            recommendations.append(recommendation)
        
        return recommendations
    
    def _create_error_response(self, request: RecommendationRequest, error_message: str, 
                             session_id: str, start_time: float) -> RecommendationResponse:
        """Create error response when processing fails"""
        processing_time = time.time() - start_time
        
        # Create minimal profile from input
        profile = UserProfile(
            recipient_age=25,
            recipient_gender="other",
            interests=["general"],
            relationship="friend",
            occasion="general",
            budget_inr=1000,
            constraints=[]
        )
        
        return RecommendationResponse(
            profile=profile,
            concepts=[],
            recommendations=[],
            explanations=[],
            summary=f"Unable to process your request due to: {error_message}",
            processing_time=processing_time,
            session_id=session_id,
            timestamp=datetime.now(),
            metadata={'error': error_message, 'error_type': 'processing_error'}
        )
    
    def _update_agent_performance(self, agent_name: str, processing_time: float, success: bool):
        """Update performance metrics for individual agents"""
        metrics = self.performance_metrics['agent_performance'][agent_name]
        
        # Update average time (simple moving average)
        current_avg = metrics['avg_time']
        total_requests = self.performance_metrics['total_requests']
        new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        metrics['avg_time'] = new_avg
        
        # Update success rate
        if not success:
            metrics['success_rate'] = (metrics['success_rate'] * (total_requests - 1)) / total_requests
    
    def _update_average_processing_time(self, processing_time: float):
        """Update overall average processing time"""
        total_requests = self.performance_metrics['total_requests']
        current_avg = self.performance_metrics['average_processing_time']
        new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        self.performance_metrics['average_processing_time'] = new_avg
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            **self.performance_metrics,
            'success_rate': (
                self.performance_metrics['successful_requests'] / 
                max(self.performance_metrics['total_requests'], 1)
            )
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all agents and system"""
        health_status = {
            'overall_status': 'healthy',
            'agents': {},
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': self.get_performance_metrics()
        }
        
        try:
            # Test each agent with minimal input
            test_input = "Test gift for friend birthday budget 1000"
            
            # Test Profile Analyzer
            try:
                profile = self.profile_analyzer.analyze(test_input)
                health_status['agents']['profile_analyzer'] = {'status': 'healthy', 'response_time': 0.1}
            except Exception as e:
                health_status['agents']['profile_analyzer'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['overall_status'] = 'degraded'
            
            # Test Creative Idea Agent
            try:
                test_profile = UserProfile(
                    recipient_age=25, recipient_gender="other", interests=["music"],
                    relationship="friend", occasion="birthday", budget_inr=1000, constraints=[]
                )
                concepts = self.creative_agent.generate_concepts(test_profile)
                health_status['agents']['creative_idea'] = {'status': 'healthy', 'response_time': 0.1}
            except Exception as e:
                health_status['agents']['creative_idea'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['overall_status'] = 'degraded'
            
            # Test Filter & Rank Agent
            try:
                ranked_products = self.filter_rank_agent.filter_and_rank(test_profile, [])
                health_status['agents']['filter_rank'] = {'status': 'healthy', 'response_time': 0.1}
            except Exception as e:
                health_status['agents']['filter_rank'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['overall_status'] = 'degraded'
            
            # Test Explanation Agent
            try:
                explanations = self.explanation_agent.generate_explanation(test_profile, [], [])
                health_status['agents']['explanation'] = {'status': 'healthy', 'response_time': 0.1}
            except Exception as e:
                health_status['agents']['explanation'] = {'status': 'unhealthy', 'error': str(e)}
                health_status['overall_status'] = 'degraded'
                
        except Exception as e:
            health_status['overall_status'] = 'unhealthy'
            health_status['system_error'] = str(e)
        
        return health_status

# Singleton instance
orchestrator = GiftRecommendationOrchestrator()

if __name__ == "__main__":
    # Test the orchestrator
    request = RecommendationRequest(
        user_input="I need a birthday gift for my brother who is 28 years old, loves music and guitar, budget is ₹2000",
        max_recommendations=3
    )
    
    response = orchestrator.get_recommendations(request)
    
    print(f"Processing Time: {response.processing_time:.2f}s")
    print(f"Recommendations: {len(response.recommendations)}")
    print(f"Summary: {response.summary}")
    print(f"Performance Metrics: {orchestrator.get_performance_metrics()}")
