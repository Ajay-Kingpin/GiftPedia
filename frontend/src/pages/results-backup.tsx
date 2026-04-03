import React from 'react';

const ResultsPage = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center p-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Results Page Working!
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          The /results route is working correctly.
        </p>
        <div className="space-y-4">
          <a 
            href="/" 
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Back to Home
          </a>
          <div className="text-sm text-gray-500 mt-4">
            <p>✅ Next.js routing is working</p>
            <p>✅ Page compilation successful</p>
            <p>✅ No missing components</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
