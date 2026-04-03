import React, { useState } from 'react';
import { RecommendationExplanation } from '../types/gift';
import GiftRecommendationCard from './GiftRecommendationCard';

interface RecommendationResultsProps {
  explanations: RecommendationExplanation[];
  summary: string;
  processingTime: number;
  onViewDetails: (productId: string) => void;
  isLoading?: boolean;
}

const RecommendationResults: React.FC<RecommendationResultsProps> = ({
  explanations,
  summary,
  processingTime,
  onViewDetails,
  isLoading = false
}) => {
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-600">Finding the perfect gifts...</p>
        <p className="text-sm text-gray-500 mt-2">This usually takes a few seconds</p>
      </div>
    );
  }

  if (explanations.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">🎁</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No recommendations found</h3>
        <p className="text-gray-600 mb-4">
          We couldn't find suitable gifts based on your criteria. Try adjusting your preferences or budget.
        </p>
        <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          Try Again
        </button>
      </div>
    );
  }

  const getOverallConfidence = (): number => {
    if (explanations.length === 0) return 0;
    const total = explanations.reduce((sum, exp) => sum + exp.confidence_score, 0);
    return total / explanations.length;
  };

  const getConfidenceColor = (score: number): string => {
    if (score >= 0.9) return 'text-green-600';
    if (score >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score: number): string => {
    if (score >= 0.9) return 'Excellent';
    if (score >= 0.7) return 'Good';
    return 'Fair';
  };

  const overallConfidence = getOverallConfidence();

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Gift Recommendations</h2>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm text-gray-500">Processing time</p>
              <p className="font-semibold">{processingTime.toFixed(2)}s</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Overall confidence</p>
              <p className={`font-semibold ${getConfidenceColor(overallConfidence)}`}>
                {getConfidenceLabel(overallConfidence)} ({Math.round(overallConfidence * 100)}%)
              </p>
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-blue-900 mb-2">Why these gifts are perfect:</h3>
          <p className="text-blue-800">{summary}</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Recommendations</p>
                <p className="text-2xl font-bold text-gray-900">{explanations.length}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg Confidence</p>
                <p className={`text-2xl font-bold ${getConfidenceColor(overallConfidence)}`}>
                  {Math.round(overallConfidence * 100)}%
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Processing Speed</p>
                <p className="text-2xl font-bold text-gray-900">Fast</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="space-y-4">
        {explanations.map((explanation) => (
          <div key={explanation.product_id}>
            <GiftRecommendationCard
              explanation={explanation}
              onViewDetails={onViewDetails}
            />
          </div>
        ))}
      </div>

      {/* Footer Actions */}
      <div className="mt-8 flex flex-col sm:flex-row gap-4">
        <button className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium">
          Get More Recommendations
        </button>
        <button className="flex-1 border border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors font-medium">
          Save All Recommendations
        </button>
        <button className="flex-1 border border-gray-300 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors font-medium">
          Share Results
        </button>
      </div>

      {/* Tips */}
      <div className="mt-8 bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 mb-3">💡 Next Steps</h3>
        <ul className="space-y-2 text-sm text-gray-600">
          <li>• Click "View Details" to see more information about each product</li>
          <li>• Check the confidence scores to understand our recommendation quality</li>
          <li>• Consider the potential concerns before making your final decision</li>
          <li>• Save your favorites to compare later</li>
          <li>• Share with friends and family to get their opinions</li>
        </ul>
      </div>
    </div>
  );
};

export default RecommendationResults;
