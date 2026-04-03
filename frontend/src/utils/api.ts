import axios from 'axios';
import { RecommendationRequest, RecommendationResponse } from '@/types/gift';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use((config) => {
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (apiKey) {
    config.headers.Authorization = `Bearer ${apiKey}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const giftRecommendationAPI = {
  getRecommendations: async (request: RecommendationRequest): Promise<RecommendationResponse> => {
    const response = await apiClient.post<RecommendationResponse>('/recommendations', request);
    return response.data;
  },

  healthCheck: async (): Promise<{ status: string }> => {
    const response = await apiClient.get<{ status: string }>('/health');
    return response.data;
  },

  getCategories: async (): Promise<Array<{ id: string; name: string; product_count: number }>> => {
    const response = await apiClient.get<Array<{ id: string; name: string; product_count: number }>>('/categories');
    return response.data;
  },

  getProductDetails: async (productId: string): Promise<any> => {
    const response = await apiClient.get<any>(`/products/${productId}`);
    return response.data;
  },

  getPopularGifts: async (category?: string, limit?: number): Promise<any[]> => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (limit) params.append('limit', limit.toString());
    
    const response = await apiClient.get<any[]>(`/popular-gifts?${params.toString()}`);
    return response.data;
  },
};

export default apiClient;
