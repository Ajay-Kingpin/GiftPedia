export interface UserProfile {
  recipient_age: number | null;
  recipient_gender: 'male' | 'female' | 'non-binary' | 'unknown';
  interests: string[];
  relationship: 'partner' | 'friend' | 'family' | 'colleague' | 'acquaintance' | 'other';
  occasion: 'birthday' | 'anniversary' | 'wedding' | 'festival' | 'corporate' | 'just_because' | 'other';
  budget_inr: number;
  constraints: string[];
}

export interface Product {
  product_id: string;
  name: string;
  category: string;
  subcategory: string;
  price_inr: number;
  brand?: string;
  image_url: string;
  affiliate_link: string;
  confidence_score?: number;
  explanation?: string;
}

export interface RecommendationRequest {
  user_input: string;
  session_id?: string;
  user_id?: string;
}

export interface RecommendationResponse {
  success: boolean;
  data?: {
    profile: UserProfile;
    concepts: GiftConcept[];
    recommendations: Product[];
    explanations: RecommendationExplanation[];
    summary: string;
    metadata: any;
  };
  processing_time?: number;
  session_id?: string;
  timestamp?: string;
  error?: string;
}

export interface RecommendationExplanation {
  product_id: string;
  product_name: string;
  explanation: string;
  key_reasons: string[];
  confidence_score: number;
  match_factors: string[];
  potential_concerns: string[];
}

export interface GiftConcept {
  concept: string;
  category: string;
  reasoning: string;
}
