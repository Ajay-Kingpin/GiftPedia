import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useRouter } from 'next/router';
import { giftRecommendationAPI } from '@/utils/api';
import { RecommendationRequest } from '@/types/gift';

interface HomePageProps {}

const HomePage: React.FC<HomePageProps> = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RecommendationRequest>();

  const onSubmit = async (data: RecommendationRequest) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await giftRecommendationAPI.getRecommendations(data);
      
      // Store data in localStorage for the results page
      localStorage.setItem('recommendations', JSON.stringify(response));
      sessionStorage.setItem('recommendations', JSON.stringify(response));
      
      // Navigate to results page
      router.push('/results');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to get recommendations. Please try again.');
      console.error('Error:', err);
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

        <div className="bg-white shadow-md rounded-lg p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div>
              <label htmlFor="user_input" className="block text-sm font-medium text-gray-700 mb-2">
                Describe the person and occasion
              </label>
              <textarea
                id="user_input"
                {...register('user_input', { 
                  required: 'Please describe who you need a gift for',
                  minLength: { 
                    value: 10, 
                    message: 'Please provide at least 10 characters' 
                  }
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={4}
                placeholder="e.g., I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000"
              />
              {errors.user_input && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.user_input.message}
                </p>
              )}
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Getting Recommendations...' : 'Get Gift Recommendations'}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-600">{error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HomePage;
