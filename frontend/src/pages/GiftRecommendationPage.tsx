import React, { useState } from 'react';
import { RecommendationExplanation } from '../types/gift';
import ConversationalInput from '../components/ConversationalInput';
import RecommendationResults from '../components/RecommendationResults';
import { getRecommendations } from '../services/api';

interface ProductDetails {
  product_id: string;
  name: string;
  category: string;
  price_inr: number;
  image_url: string;
  affiliate_link: string;
  description?: string;
  specifications?: Record<string, any>;
  reviews?: Array<{
    rating: number;
    comment: string;
    author: string;
    date: string;
  }>;
}

const GiftRecommendationPage: React.FC = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [explanations, setExplanations] = useState<RecommendationExplanation[]>([]);
  const [summary, setSummary] = useState('');
  const [processingTime, setProcessingTime] = useState(0);
  const [selectedProduct, setSelectedProduct] = useState<ProductDetails | null>(null);
  const [showProductModal, setShowProductModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (userInput: string) => {
    setIsProcessing(true);
    setError(null);
    setExplanations([]);
    setSummary('');
    
    const startTime = Date.now();
    
    try {
      const response = await getRecommendations(userInput);
      
      // Mock response for now - replace with actual API call
      const mockResponse = {
        explanations: [
          {
            product_id: "prod_001",
            product_name: "Fender Custom Guitar Strap",
            explanation: "This premium guitar strap is perfect for music enthusiasts who value comfort and style. It combines quality craftsmanship with practical functionality, making it an ideal gift for guitar players.",
            key_reasons: [
              "High-quality leather construction",
              "Adjustable length for comfort",
              "Perfect for guitar enthusiasts",
              "Premium brand reputation",
              "Great value for money"
            ],
            confidence_score: 0.92,
            match_factors: [
              "Interest alignment",
              "Budget compatibility",
              "Quality brand",
              "Occasion appropriateness"
            ],
            potential_concerns: [
              "May require additional hardware",
              "Leather needs initial break-in period"
            ]
          },
          {
            product_id: "prod_002",
            product_name: "Professional Music Stand",
            explanation: "A sturdy and adjustable music stand that's perfect for musicians of all levels. It provides excellent stability for sheet music and tablets during practice sessions.",
            key_reasons: [
              "Sturdy construction",
              "Adjustable height",
              "Portable design",
              "Professional appearance",
              "Essential for musicians"
            ],
            confidence_score: 0.85,
            match_factors: [
              "Interest match",
              "Practical utility",
              "Professional quality"
            ],
            potential_concerns: [
              "Assembly required",
              "Takes up storage space"
            ]
          }
        ],
        summary: "Based on the recipient's passion for music and guitar, we've selected high-quality accessories that enhance their musical experience. These recommendations focus on practical items that combine functionality with premium quality, perfect for a serious musician.",
        processing_time: 2.3
      };
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setExplanations(mockResponse.explanations);
      setSummary(mockResponse.summary);
      setProcessingTime(mockResponse.processing_time);
      
    } catch (err) {
      setError('Failed to get recommendations. Please try again.');
      console.error('Error getting recommendations:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleViewDetails = async (productId: string) => {
    try {
      // Mock product details - replace with actual API call
      const mockProductDetails: ProductDetails = {
        product_id: productId,
        name: "Fender Custom Guitar Strap",
        category: "Music & Instruments",
        subcategory: "Guitar Accessories",
        price_inr: 1899.0,
        image_url: "https://images.unsplash.com/photo-1592514258948-18e124862534?w=400",
        affiliate_link: "https://example.com/affiliate/fender-strap",
        description: "Premium leather guitar strap with adjustable length and comfortable padding. Perfect for long practice sessions and performances.",
        specifications: {
          "Material": "Genuine Leather",
          "Length": "Adjustable 38-60 inches",
          "Width": "2.5 inches",
          "Padding": "Memory foam",
          "Colors": "Black, Brown, Tan"
        },
        reviews: [
          {
            rating: 5,
            comment: "Best guitar strap I've ever used! Very comfortable and durable.",
            author: "John D.",
            date: "2024-01-15"
          },
          {
            rating: 4,
            comment: "Great quality, though a bit pricey. Worth it for serious musicians.",
            author: "Sarah M.",
            date: "2024-01-10"
          }
        ]
      };
      
      setSelectedProduct(mockProductDetails);
      setShowProductModal(true);
      
    } catch (err) {
      console.error('Error fetching product details:', err);
    }
  };

  const closeModal = () => {
    setShowProductModal(false);
    setSelectedProduct(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">GiftPedia</h1>
              <span className="ml-2 text-sm text-gray-500">AI-Powered Gift Recommendations</span>
            </div>
            <nav className="flex space-x-8">
              <a href="#" className="text-gray-700 hover:text-gray-900">Home</a>
              <a href="#" className="text-gray-700 hover:text-gray-900">About</a>
              <a href="#" className="text-gray-700 hover:text-gray-900">Contact</a>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Find the Perfect Gift with AI
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our intelligent recommendation system analyzes the recipient's profile, interests, 
            and your preferences to suggest personalized gift recommendations with confidence scores.
          </p>
        </div>

        {/* Input Section */}
        <div className="mb-12">
          <ConversationalInput
            onSubmit={handleSubmit}
            isLoading={isProcessing}
            placeholder="Tell me about the person you're shopping for..."
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Results Section */}
        {(explanations.length > 0 || isProcessing) && (
          <RecommendationResults
            explanations={explanations}
            summary={summary}
            processingTime={processingTime}
            onViewDetails={handleViewDetails}
            isLoading={isProcessing}
          />
        )}

        {/* Features Section */}
        {explanations.length === 0 && !isProcessing && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Analysis</h3>
              <p className="text-gray-600">Our AI analyzes multiple factors to find the perfect match</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Confidence Scoring</h3>
              <p className="text-gray-600">Get confidence scores and detailed explanations for each recommendation</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Fast Results</h3>
              <p className="text-gray-600">Get personalized recommendations in seconds, not hours</p>
            </div>
          </div>
        )}
      </main>

      {/* Product Details Modal */}
      {showProductModal && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
              <h3 className="text-xl font-semibold">{selectedProduct.name}</h3>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <img
                    src={selectedProduct.image_url}
                    alt={selectedProduct.name}
                    className="w-full h-64 object-cover rounded-lg"
                  />
                </div>
                
                <div>
                  <div className="mb-4">
                    <span className="text-sm text-gray-500">{selectedProduct.category}</span>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedProduct.name}</h2>
                    <p className="text-3xl font-bold text-blue-600">₹{selectedProduct.price_inr}</p>
                  </div>
                  
                  <p className="text-gray-700 mb-6">{selectedProduct.description}</p>
                  
                  {selectedProduct.specifications && (
                    <div className="mb-6">
                      <h4 className="font-semibold text-gray-900 mb-2">Specifications</h4>
                      <dl className="grid grid-cols-2 gap-2">
                        {Object.entries(selectedProduct.specifications).map(([key, value]) => (
                          <div key={key}>
                            <dt className="text-sm text-gray-500">{key}</dt>
                            <dd className="text-sm font-medium">{value}</dd>
                          </div>
                        ))}
                      </dl>
                    </div>
                  )}
                  
                  <div className="flex space-x-4">
                    <a
                      href={selectedProduct.affiliate_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors text-center font-medium"
                    >
                      Buy Now
                    </a>
                    <button className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium">
                      Save for Later
                    </button>
                  </div>
                </div>
              </div>
              
              {selectedProduct.reviews && (
                <div className="mt-8">
                  <h4 className="font-semibold text-gray-900 mb-4">Customer Reviews</h4>
                  <div className="space-y-4">
                    {selectedProduct.reviews.map((review, index) => (
                      <div key={index} className="border-b pb-4">
                        <div className="flex items-center mb-2">
                          <div className="flex text-yellow-400">
                            {[...Array(5)].map((_, i) => (
                              <svg
                                key={i}
                                className={`w-4 h-4 ${i < review.rating ? 'text-yellow-400' : 'text-gray-300'}`}
                                fill="currentColor"
                                viewBox="0 0 20 20"
                              >
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                              </svg>
                            ))}
                          </div>
                          <span className="ml-2 text-sm font-medium">{review.author}</span>
                          <span className="ml-2 text-sm text-gray-500">{review.date}</span>
                        </div>
                        <p className="text-gray-700">{review.comment}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GiftRecommendationPage;
