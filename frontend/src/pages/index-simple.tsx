import React, { useState } from 'react';

const SimpleHomePage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    const formData = new FormData(e.currentTarget);
    const userInput = formData.get('userInput') as string;

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Store mock data in localStorage
      const mockResponse = {
        success: true,
        data: {
          recommendations: [
            {
              product_id: "prod_001",
              name: "Fender Guitar Strap",
              category: "Music & Instruments",
              price_inr: 1899,
              brand: "Fender",
              image_url: "https://picsum.photos/seed/fender-strap/400/300.jpg",
              final_score: 0.8
            },
            {
              product_id: "prod_002", 
              name: "Wireless Headphones",
              category: "Electronics",
              price_inr: 2499,
              brand: "Sony",
              image_url: "https://picsum.photos/seed/headphones/400/300.jpg",
              final_score: 0.7
            }
          ],
          summary: "Found 2 personalized gift recommendations based on your request."
        },
        processing_time: 1.0
      };

      localStorage.setItem('recommendations', JSON.stringify(mockResponse));
      setSuccess(true);
      
      // Navigate to results page
      window.location.href = '/results';
      
    } catch (err) {
      setError('Failed to get recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            GiftPedia
          </h1>
          <p className="text-lg text-gray-600">
            Find the perfect gift with AI-powered recommendations
          </p>
        </div>

        <div className="bg-white shadow-lg rounded-lg p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">
            Tell us about the gift you're looking for
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="userInput" className="block text-sm font-medium text-gray-700 mb-2">
                Describe your gift idea
              </label>
              <textarea
                id="userInput"
                name="userInput"
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Birthday gift for brother who loves music, budget ₹2000"
                defaultValue="Birthday gift for brother who loves music, budget ₹2000"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
                {error}
              </div>
            )}

            {success && (
              <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
                Success! Redirecting to results...
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Getting Recommendations...
                  </span>
                ) : (
                  'Get Gift Recommendations'
                )}
              </button>
            </div>
          </form>
        </div>

        <div className="mt-8 text-center">
          <a 
            href="/results" 
            className="text-blue-600 hover:text-blue-800 underline"
          >
            Or view sample results →
          </a>
        </div>
      </div>
    </div>
  );
};

export default SimpleHomePage;
