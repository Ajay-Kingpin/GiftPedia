import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import RecommendationResults from '@/components/RecommendationResults';
import { RecommendationResponse } from '@/types/gift';

const ResultsPage: React.FC = () => {
  const router = useRouter();
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!router.isReady) return;

    // Try multiple methods to get the data
    let data: any = null;

    // Method 1: Check localStorage first (most reliable)
    try {
      const storedData = localStorage.getItem('recommendations');
      if (storedData) {
        data = JSON.parse(storedData);
        console.log('Loaded data from localStorage');
      }
    } catch (err) {
      console.warn('Failed to load from localStorage:', err);
    }

    // Method 2: Check URL query parameters (fallback)
    if (!data) {
      const { data: queryData } = router.query;
      if (queryData && typeof queryData === 'string') {
        try {
          // Handle URL encoding
          let decodedData = queryData;
          try {
            decodedData = decodeURIComponent(queryData);
          } catch (decodeErr) {
            console.warn('URL decode failed, using original data:', decodeErr);
          }
          
          // Try to parse JSON
          data = JSON.parse(decodedData);
          console.log('Loaded data from URL query');
        } catch (err) {
          console.error('Error parsing URL data:', err);
          console.error('Raw data:', queryData.substring(0, 200) + '...');
        }
      }
    }

    // Method 3: Check session storage (another fallback)
    if (!data) {
      try {
        const sessionData = sessionStorage.getItem('recommendations');
        if (sessionData) {
          data = JSON.parse(sessionData);
          console.log('Loaded data from sessionStorage');
        }
      } catch (err) {
        console.warn('Failed to load from sessionStorage:', err);
      }
    }

    if (data) {
      setRecommendations(data);
      setError(null);
    } else {
      setError('No recommendations data found. Please go back and submit a new request.');
    }
    
    setLoading(false);
  }, [router.isReady, router.query]);

  const handleViewDetails = (productId: string) => {
    console.log('View details for product:', productId);
    // TODO: Implement product details modal or navigation
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading recommendations...</p>
        </div>
      </div>
    );
  }

  if (error || !recommendations) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-600 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Recommendations</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-y-3">
            <button
              onClick={() => router.push('/')}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Go Back to Homepage
            </button>
            <div className="text-sm text-gray-500">
              <p>If the problem persists, please try:</p>
              <ul className="mt-2 text-left">
                <li>• Refreshing the page</li>
                <li>• Submitting a new request</li>
                <li>• Checking your internet connection</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <RecommendationResults
        explanations={recommendations.data?.explanations || []}
        summary={recommendations.data?.summary || ''}
        processingTime={recommendations.processing_time || 0}
        onViewDetails={handleViewDetails}
        isLoading={false}
      />
    </div>
  );
};

export default ResultsPage;
