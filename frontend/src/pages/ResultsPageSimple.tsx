import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

const ResultsPageSimple = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!router.isReady) return;

    // Try to get data from localStorage
    try {
      const storedData = localStorage.getItem('recommendations');
      if (storedData) {
        const parsedData = JSON.parse(storedData);
        setData(parsedData);
        console.log('Successfully loaded recommendations from localStorage');
      } else {
        setError('No recommendations found in localStorage');
      }
    } catch (err) {
      console.error('Error loading recommendations:', err);
      setError('Failed to load recommendations');
    }
    
    setLoading(false);
  }, [router.isReady]);

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

  if (error || !data) {
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
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            Go Back to Homepage
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Your Gift Recommendations
          </h1>
          <p className="text-lg text-gray-600">
            Found {data?.data?.recommendations?.length || 0} personalized recommendations
          </p>
        </div>

        {/* Display recommendations */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {data?.data?.recommendations?.map((product: any, index: number) => (
            <div key={product.product_id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="aspect-w-16 aspect-h-9 bg-gray-200">
                <img 
                  src={product.image_url} 
                  alt={product.name}
                  className="w-full h-48 object-cover"
                  onError={(e) => {
                    e.currentTarget.src = 'https://picsum.photos/seed/gift/400/300.jpg';
                  }}
                />
              </div>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {product.name}
                </h3>
                <p className="text-gray-600 mb-4">
                  {product.category} • {product.brand}
                </p>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-2xl font-bold text-blue-600">
                    ₹{product.price_inr}
                  </span>
                  <span className="text-sm text-gray-500">
                    Score: {(product.final_score * 100).toFixed(0)}%
                  </span>
                </div>
                <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        {data?.data?.summary && (
          <div className="mt-8 bg-blue-50 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-blue-900 mb-2">Summary</h2>
            <p className="text-blue-800">{data.data.summary}</p>
          </div>
        )}

        {/* Processing time */}
        {data?.processing_time && (
          <div className="mt-4 text-center text-sm text-gray-500">
            Processing time: {data.processing_time.toFixed(2)} seconds
          </div>
        )}

        <div className="mt-8 text-center">
          <button
            onClick={() => router.push('/')}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
          >
            Get More Recommendations
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsPageSimple;
