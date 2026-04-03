import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import HomePage from '@/pages/HomePage';
import { giftRecommendationAPI } from '@/utils/api';

// Mock the API module
jest.mock('@/utils/api');
const mockedAPI = giftRecommendationAPI as jest.Mocked<typeof giftRecommendationAPI>;

// Mock react-hook-form
jest.mock('react-hook-form', () => ({
  useForm: () => ({
    register: jest.fn(),
    handleSubmit: (fn: Function) => fn,
    formState: { errors: {} },
  }),
}));

describe('HomePage Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the main heading and description', () => {
    render(<HomePage />);
    
    expect(screen.getByText('GiftPedia')).toBeInTheDocument();
    expect(screen.getByText('Find perfect gift with AI-powered recommendations')).toBeInTheDocument();
  });

  it('renders the input form with correct elements', () => {
    render(<HomePage />);
    
    const textarea = screen.getByLabelText('Describe person and occasion');
    const button = screen.getByRole('button', { name: 'Get Gift Recommendations' });
    
    expect(textarea).toBeInTheDocument();
    expect(button).toBeInTheDocument();
    expect(textarea).toHaveAttribute('placeholder', 'e.g., I need a birthday gift for my brother, a 28-year-old musician, budget is ₹2000');
  });

  it('submits form with correct data', async () => {
    const user = userEvent.setup();
    const mockResponse = {
      recommendations: [
        {
          product_id: 'prod_1',
          name: 'Test Product',
          price_inr: 1000,
          confidence_score: 5
        }
      ],
      profile: {
        recipient_age: 28,
        interests: ['music']
      },
      processing_time: 1.5,
      session_id: 'test-session'
    };

    mockedAPI.getRecommendations.mockResolvedValue(mockResponse);

    render(<HomePage />);
    
    const textarea = screen.getByLabelText('Describe person and occasion');
    const button = screen.getByRole('button', { name: 'Get Gift Recommendations' });

    await user.type(textarea, 'I need a birthday gift for my brother, a 28-year-old musician');
    await user.click(button);

    await waitFor(() => {
      expect(mockedAPI.getRecommendations).toHaveBeenCalledWith({
        user_input: 'I need a birthday gift for my brother, a 28-year-old musician',
        session_id: undefined,
        user_id: undefined
      });
    });
  });

  it('shows loading state while submitting', async () => {
    const user = userEvent.setup();
    mockedAPI.getRecommendations.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<HomePage />);
    
    const textarea = screen.getByLabelText('Describe person and occasion');
    const button = screen.getByRole('button', { name: 'Get Gift Recommendations' });

    await user.type(textarea, 'Test input');
    await user.click(button);

    expect(screen.getByText('Getting Recommendations...')).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  it('displays error message when API call fails', async () => {
    const user = userEvent.setup();
    mockedAPI.getRecommendations.mockRejectedValue(new Error('API Error'));

    render(<HomePage />);
    
    const textarea = screen.getByLabelText('Describe person and occasion');
    const button = screen.getByRole('button', { name: 'Get Gift Recommendations' });

    await user.type(textarea, 'Test input');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Failed to get recommendations. Please try again.')).toBeInTheDocument();
    });
  });

  it('clears error message on successful submission', async () => {
    const user = userEvent.setup();
    mockedAPI.getRecommendations
      .mockRejectedValueOnce(new Error('First error'))
      .mockResolvedValueOnce({
        recommendations: [],
        profile: {},
        processing_time: 1,
        session_id: 'test'
      });

    render(<HomePage />);
    
    const textarea = screen.getByLabelText('Describe person and occasion');
    const button = screen.getByRole('button', { name: 'Get Gift Recommendations' });

    // First submission - should show error
    await user.type(textarea, 'Test input');
    await user.click(button);

    await waitFor(() => {
      expect(screen.getByText('Failed to get recommendations. Please try again.')).toBeInTheDocument();
    });

    // Second submission - should clear error
    await user.click(button);

    await waitFor(() => {
      expect(screen.queryByText('Failed to get recommendations. Please try again.')).not.toBeInTheDocument();
    });
  });
});
