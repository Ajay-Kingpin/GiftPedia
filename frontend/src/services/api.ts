import { RecommendationRequest, RecommendationResponse, RecommendationExplanation } from '../types/gift';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json() as T;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async getRecommendations(userInput: string): Promise<{
    explanations: RecommendationExplanation[];
    summary: string;
    processing_time: number;
  }> {
    const request: RecommendationRequest = {
      user_input: userInput,
    };

    return this.request('/recommendations', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getProductDetails(productId: string): Promise<{
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
  }> {
    return this.request(`/products/${productId}`);
  }

  async saveRecommendations(recommendations: RecommendationExplanation[]): Promise<{
    saved_count: number;
    session_id: string;
  }> {
    return this.request('/save-recommendations', {
      method: 'POST',
      body: JSON.stringify({ recommendations }),
    });
  }

  async getSavedRecommendations(sessionId: string): Promise<{
    recommendations: RecommendationExplanation[];
    created_at: string;
  }> {
    return this.request(`/saved-recommendations/${sessionId}`);
  }

  async shareRecommendations(recommendations: RecommendationExplanation[], message?: string): Promise<{
    share_url: string;
    expires_at: string;
  }> {
    return this.request('/share-recommendations', {
      method: 'POST',
      body: JSON.stringify({ recommendations, message }),
    });
  }

  async getSharedRecommendations(shareId: string): Promise<{
    recommendations: RecommendationExplanation[];
    message?: string;
    created_at: string;
  }> {
    return this.request(`/shared-recommendations/${shareId}`);
  }

  async trackEvent(event: string, data: Record<string, any>): Promise<void> {
    try {
      await this.request('/analytics', {
        method: 'POST',
        body: JSON.stringify({ event, data }),
      });
    } catch (error) {
      // Don't throw errors for analytics failures
      console.warn('Analytics tracking failed:', error);
    }
  }

  async getPopularGifts(category?: string): Promise<Array<{
    product_id: string;
    name: string;
    category: string;
    price_inr: number;
    image_url: string;
    popularity_score: number;
  }>> {
    const params = category ? `?category=${encodeURIComponent(category)}` : '';
    return this.request(`/popular-gifts${params}`);
  }

  async searchProducts(query: string, filters?: {
    category?: string;
    min_price?: number;
    max_price?: number;
    brand?: string;
  }): Promise<Array<{
    product_id: string;
    name: string;
    category: string;
    price_inr: number;
    image_url: string;
    affiliate_link: string;
  }>> {
    const params = new URLSearchParams({
      q: query,
      ...filters,
    });
    
    return this.request(`/search?${params.toString()}`);
  }

  async getCategories(): Promise<Array<{
    id: string;
    name: string;
    description: string;
    product_count: number;
  }>> {
    return this.request('/categories');
  }

  async getBrands(): Promise<Array<{
    id: string;
    name: string;
    logo_url?: string;
    product_count: number;
  }>> {
    return this.request('/brands');
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export convenience functions
export const getRecommendations = (userInput: string) => 
  apiService.getRecommendations(userInput);

export const getProductDetails = (productId: string) => 
  apiService.getProductDetails(productId);

export const saveRecommendations = (recommendations: RecommendationExplanation[]) => 
  apiService.saveRecommendations(recommendations);

export const getSavedRecommendations = (sessionId: string) => 
  apiService.getSavedRecommendations(sessionId);

export const shareRecommendations = (recommendations: RecommendationExplanation[], message?: string) => 
  apiService.shareRecommendations(recommendations, message);

export const getSharedRecommendations = (shareId: string) => 
  apiService.getSharedRecommendations(shareId);

export const trackEvent = (event: string, data: Record<string, any>) => 
  apiService.trackEvent(event, data);

export const getPopularGifts = (category?: string) => 
  apiService.getPopularGifts(category);

export const searchProducts = (query: string, filters?: any) => 
  apiService.searchProducts(query, filters);

export const getCategories = () => 
  apiService.getCategories();

export const getBrands = () => 
  apiService.getBrands();
