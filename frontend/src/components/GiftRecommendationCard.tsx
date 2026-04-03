import React from 'react';
import { RecommendationExplanation } from '../../types/gift';

interface GiftRecommendationCardProps {
  explanation: RecommendationExplanation;
  onViewDetails: (productId: string) => void;
}

const GiftRecommendationCard: React.FC<GiftRecommendationCardProps> = ({
  explanation,
  onViewDetails
}) => {
  const getConfidenceColor = (score: number): string => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score: number): string => {
    if (score >= 0.9) return 'Excellent Match';
    if (score >= 0.7) return 'Good Match';
    return 'Fair Match';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4 border border-gray-200 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {explanation.product_name}
          </h3>
          
          {/* Confidence Score */}
          <div className="flex items-center space-x-2 mb-3">
            <div className="flex items-center">
              <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
              <span className={`font-medium ${getConfidenceColor(explanation.confidence_score)}`}>
                {getConfidenceLabel(explanation.confidence_score)}
              </span>
            </div>
            <span className="text-sm text-gray-500">
              ({Math.round(explanation.confidence_score * 100)}% confidence)
            </span>
          </div>
        </div>
        
        {/* Confidence Badge */}
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(explanation.confidence_score)} bg-opacity-10`}>
          {Math.round(explanation.confidence_score * 100)}%
        </div>
      </div>

      {/* Explanation */}
      <div className="mb-4">
        <p className="text-gray-700 leading-relaxed">
          {explanation.explanation}
        </p>
      </div>

      {/* Key Reasons */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-2">Why this gift is perfect:</h4>
        <ul className="space-y-1">
          {explanation.key_reasons.map((reason: string, index: number) => (
            <li key={index} className="flex items-start">
              <svg className="w-4 h-4 text-green-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-gray-600">{reason}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Match Factors */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-2">Match Factors:</h4>
        <div className="flex flex-wrap gap-2">
          {explanation.match_factors.map((factor: string, index: number) => (
            <span
              key={index}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {factor}
            </span>
          ))}
        </div>
      </div>

      {/* Potential Concerns */}
      {explanation.potential_concerns.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-900 mb-2">Things to Consider:</h4>
          <ul className="space-y-1">
            {explanation.potential_concerns.map((concern: string, index: number) => (
              <li key={index} className="flex items-start">
                <svg className="w-4 h-4 text-yellow-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-gray-600">{concern}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex space-x-3">
        <button
          onClick={() => onViewDetails(explanation.product_id)}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          View Details
        </button>
        <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium">
          Save for Later
        </button>
      </div>
    </div>
  );
};

export default GiftRecommendationCard;
