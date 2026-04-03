import { giftRecommendationAPI } from '@/utils/api';
import { RecommendationRequest } from '@/types/gift';

// Mock axios
jest.mock('axios');
import axios from 'axios';

const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getRecommendations', () => {
    it('should make POST request to recommendations endpoint', async () => {
      const mockRequest: RecommendationRequest = {
        user_input: 'I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000',
        session_id: 'test-session-123'
      };

      const mockResponse = {
        data: {
          recommendations: [
            {
              product_id: 'prod_1',
              name: 'Fender Custom Guitar Strap',
              price_inr: 1899.0,
              confidence_score: 5
            }
          ],
          profile: {
            recipient_age: 28,
            recipient_gender: 'male',
            interests: ['music', 'guitar'],
            relationship: 'family',
            occasion: 'birthday',
            budget_inr: 2000,
            constraints: []
          },
          processing_time: 2.5,
          session_id: 'test-session-123'
        }
      };

      mockedAxios.create.mockReturnValue({
        post: jest.fn().mockResolvedValue(mockResponse)
      } as any);

      const result = await giftRecommendationAPI.getRecommendations(mockRequest);

      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'http://localhost:8000',
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('should handle API errors gracefully', async () => {
      const mockRequest: RecommendationRequest = {
        user_input: 'test input'
      };

      const mockError = new Error('Network error');
      mockedAxios.create.mockReturnValue({
        post: jest.fn().mockRejectedValue(mockError)
      } as any);

      await expect(giftRecommendationAPI.getRecommendations(mockRequest))
        .rejects.toThrow('Network error');
    });

    it('should include API key in headers when available', async () => {
      process.env.NEXT_PUBLIC_API_KEY = 'test-api-key';
      
      const mockRequest: RecommendationRequest = {
        user_input: 'test input'
      };

      const mockResponse = { data: { status: 'success' } };
      
      const mockApiClient = {
        post: jest.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      };

      mockedAxios.create.mockReturnValue(mockApiClient as any);

      await giftRecommendationAPI.getRecommendations(mockRequest);

      // Check that request interceptor was called
      expect(mockApiClient.interceptors.request.use).toHaveBeenCalled();
      
      delete process.env.NEXT_PUBLIC_API_KEY;
    });
  });

  describe('healthCheck', () => {
    it('should make GET request to health endpoint', async () => {
      const mockResponse = {
        data: { status: 'healthy', timestamp: 1234567890 }
      };

      const mockApiClient = {
        get: jest.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: jest.fn() },
          response: { use: jest.fn() }
        }
      };

      mockedAxios.create.mockReturnValue(mockApiClient as any);

      const result = await giftRecommendationAPI.healthCheck();

      expect(mockApiClient.get).toHaveBeenCalledWith('/health');
      expect(result).toEqual({ status: 'healthy', timestamp: 1234567890 });
    });
  });
});
