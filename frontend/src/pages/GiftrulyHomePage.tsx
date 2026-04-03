import React, { useState, useEffect } from 'react';
import { giftRecommendationAPI } from '../utils/api';

interface GiftRequest {
  occasion: string;
  recipient: string;
  age?: string;
  interests: string;
  budget: string;
  additionalInfo?: string;
}

interface Step {
  id: string;
  title: string;
  description: string;
  icon: string;
}

const GiftrulyHomePage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [giftRequest, setGiftRequest] = useState<GiftRequest>({
    occasion: '',
    recipient: '',
    interests: '',
    budget: ''
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [showResults, setShowResults] = useState(false);

  const steps: Step[] = [
    {
      id: 'occasion',
      title: 'Choose Occasion',
      description: 'What are you celebrating?',
      icon: '🎉'
    },
    {
      id: 'recipient',
      title: 'Select Recipient',
      description: 'Who is this gift for?',
      icon: '👥'
    },
    {
      id: 'details',
      title: 'Add Details',
      description: 'Tell us more about them',
      icon: '📝'
    },
    {
      id: 'budget',
      title: 'Set Budget',
      description: 'What\'s your price range?',
      icon: '💰'
    }
  ];

  const occasions = [
    { id: 'birthday', title: 'Birthday', icon: '🎂', description: 'Celebrate their special day' },
    { id: 'anniversary', title: 'Anniversary', icon: '💑', description: 'Mark your love story' },
    { id: 'valentines', title: 'Valentine\'s Day', icon: '💝', description: 'Show your love' },
    { id: 'christmas', title: 'Christmas', icon: '🎄', description: 'Holiday magic' },
    { id: 'wedding', title: 'Wedding', icon: '💒', description: 'Celebrate new beginnings' },
    { id: 'graduation', title: 'Graduation', icon: '🎓', description: 'Mark their achievement' },
    { id: 'mothers-day', title: 'Mother\'s Day', icon: '🌸', description: 'Honor mom' },
    { id: 'fathers-day', title: 'Father\'s Day', icon: '👔', description: 'Celebrate dad' }
  ];

  const recipients = [
    { id: 'mother', title: 'Mother', icon: '👩', description: 'For the woman who raised you' },
    { id: 'father', title: 'Father', icon: '👨', description: 'For the man who guided you' },
    { id: 'sister', title: 'Sister', icon: '👧', description: 'For your sister' },
    { id: 'brother', title: 'Brother', icon: '👦', description: 'For your brother' },
    { id: 'girlfriend', title: 'Girlfriend', icon: '💑', description: 'For your partner' },
    { id: 'boyfriend', title: 'Boyfriend', icon: '💑', description: 'For your partner' },
    { id: 'friend', title: 'Friend', icon: '👫', description: 'For your friend' },
    { id: 'colleague', title: 'Colleague', icon: '💼', description: 'For your coworker' }
  ];

  const handleStepChange = (stepId: string) => {
    const stepIndex = steps.findIndex(step => step.id === stepId);
    if (stepIndex !== -1) {
      setCurrentStep(stepIndex + 1);
    }
  };

  const handleOccasionSelect = (occasionId: string) => {
    setGiftRequest(prev => ({ ...prev, occasion: occasionId }));
    setCurrentStep(3);
  };

  const handleRecipientSelect = (recipientId: string) => {
    setGiftRequest(prev => ({ ...prev, recipient: recipientId }));
    setCurrentStep(4);
  };

  const handleInputChange = (field: keyof GiftRequest, value: string) => {
    setGiftRequest(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await giftRecommendationAPI.getRecommendations(giftRequest);
      setResults(response.data.recommendations);
      setShowResults(true);
    } catch (error) {
      console.error('Error getting recommendations:', error);
      alert('Sorry, something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setCurrentStep(1);
    setGiftRequest({
      occasion: '',
      recipient: '',
      interests: '',
      budget: ''
    });
    setShowResults(false);
    setResults([]);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="form-section active">
            <h3>What are you celebrating?</h3>
            <p className="mb-2">Choose the occasion to find the perfect gift.</p>
            <div className="option-cards">
              {occasions.map(occasion => (
                <div
                  key={occasion.id}
                  className="option-card"
                  onClick={() => handleOccasionSelect(occasion.id)}
                >
                  <span className="option-icon">{occasion.icon}</span>
                  <div className="option-title">{occasion.title}</div>
                  <div className="option-description">{occasion.description}</div>
                </div>
              ))}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="form-section active">
            <h3>Who is this gift for?</h3>
            <p className="mb-2">Select your relationship to the recipient.</p>
            <div className="option-cards">
              {recipients.map(recipient => (
                <div
                  key={recipient.id}
                  className="option-card"
                  onClick={() => handleRecipientSelect(recipient.id)}
                >
                  <span className="option-icon">{recipient.icon}</span>
                  <div className="option-title">{recipient.title}</div>
                  <div className="option-description">{recipient.description}</div>
                </div>
              ))}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="form-section active">
            <h3>Tell us more about them</h3>
            <p className="mb-2">Help us find the perfect gift with more details.</p>
            <div className="form-group">
              <label className="form-label">Age (optional)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., 25 years old"
                value={giftRequest.age || ''}
                onChange={(e) => handleInputChange('age', e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Interests & Hobbies *</label>
              <textarea
                className="form-textarea"
                placeholder="e.g., loves music, enjoys cooking, likes hiking, tech enthusiast..."
                value={giftRequest.interests}
                onChange={(e) => handleInputChange('interests', e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Additional Information (optional)</label>
              <textarea
                className="form-textarea"
                placeholder="Any other details that might help us find the perfect gift..."
                value={giftRequest.additionalInfo || ''}
                onChange={(e) => handleInputChange('additionalInfo', e.target.value)}
              />
            </div>
            <div className="text-center">
              <button className="btn btn-secondary" onClick={() => setCurrentStep(4)}>
                Continue to Budget
              </button>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="form-section active">
            <h3>What's your budget?</h3>
            <p className="mb-2">Set your price range for better recommendations.</p>
            <div className="form-group">
              <label className="form-label">Budget Range *</label>
              <select
                className="form-select"
                value={giftRequest.budget}
                onChange={(e) => handleInputChange('budget', e.target.value)}
                required
              >
                <option value="">Select budget range</option>
                <option value="0-50">Under $50</option>
                <option value="50-100">$50 - $100</option>
                <option value="100-200">$100 - $200</option>
                <option value="200-500">$200 - $500</option>
                <option value="500-1000">$500 - $1,000</option>
                <option value="1000+">Over $1,000</option>
              </select>
            </div>
            <div className="text-center">
              <button className="btn btn-primary btn-large" onClick={handleSubmit}>
                {loading ? (
                  <div className="loading">
                    <div className="spinner"></div>
                    Finding Perfect Gifts...
                  </div>
                ) : (
                  '🎁 Find Perfect Gifts'
                )}
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (showResults) {
    return (
      <div className="container">
        <div className="results-section">
          <div className="results-header">
            <h2>🎁 Perfect Gift Recommendations</h2>
            <p>Based on your preferences, here are our top suggestions:</p>
          </div>
          <div className="results-grid">
            {results.map((product, index) => (
              <div key={index} className="product-card">
                <img 
                  src={product.image_url || `https://picsum.photos/seed/gift${index}/400/300.jpg`} 
                  alt={product.name}
                  className="product-image"
                />
                <div className="product-content">
                  <h3 className="product-title">{product.name}</h3>
                  <div className="product-brand">{product.brand}</div>
                  <div className="product-price">
                    ${product.price}
                    {product.original_price && (
                      <span className="original">${product.original_price}</span>
                    )}
                  </div>
                  <div className={`product-availability ${product.availability === 'In Stock' ? 'in-stock' : 'out-of-stock'}`}>
                    {product.availability === 'In Stock' ? '✓ In Stock' : 'Out of Stock'}
                  </div>
                  {product.price_drop && (
                    <div className="price-drop">
                      📉 {product.price_drop}% OFF
                    </div>
                  )}
                  <div className="product-features">
                    {product.features?.slice(0, 3).map((feature: string, idx: number) => (
                      <span key={idx} className="feature-tag">{feature}</span>
                    ))}
                  </div>
                  <div className="product-actions">
                    <button className="btn btn-primary">
                      🛒 View Details
                    </button>
                    {product.affiliate_url && (
                      <a 
                        href={product.affiliate_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="btn btn-success"
                      >
                        💰 Shop Now
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="text-center mt-3">
            <button className="btn btn-secondary" onClick={resetForm}>
              🔙 Start Over
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Navigation */}
      <nav className="navbar">
        <div className="navbar-content">
          <a href="/" className="logo">
            🎁 GiftPedia
          </a>
          <div className="nav-links">
            <a href="/gift-finder" className="nav-link active">Gift Finder</a>
            <a href="/articles" className="nav-link">Articles</a>
            <a href="/about" className="nav-link">About</a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1>Let GiftPedia Find Perfect Gifts</h1>
          <p>
            Find gifts that truly matter for every occasion with our AI-Powered Gift Finder
          </p>
          <div className="text-center">
            <a href="#gift-finder" className="btn btn-primary btn-large">
              🎁 Find a Gift Now
            </a>
          </div>
        </div>
      </section>

      {/* Gift Finder Section */}
      <section id="gift-finder" className="container">
        <div className="gift-finder">
          <h2>AI-Powered Gift Finder</h2>
          
          {/* Step Navigation */}
          <div className="step-nav">
            {steps.map((step, index) => (
              <button
                key={step.id}
                className={`step-btn ${currentStep === index + 1 ? 'active' : ''}`}
                onClick={() => setCurrentStep(index + 1)}
              >
                <span>{step.icon}</span>
                {step.title}
              </button>
            ))}
          </div>

          {/* Step Content */}
          {renderStepContent()}
        </div>
      </section>

      {/* Features Section */}
      <section className="container mt-3">
        <div className="text-center mb-2">
          <h2>Why Choose GiftPedia?</h2>
        </div>
        <div className="option-cards">
          <div className="option-card">
            <span className="option-icon">🤖</span>
            <div className="option-title">AI-Powered</div>
            <div className="option-description">Cutting edge 4-agent AI system for perfect recommendations</div>
          </div>
          <div className="option-card">
            <span className="option-icon">💰</span>
            <div className="option-title">100% Free</div>
            <div className="option-description">No hidden fees, no premium features, no account required</div>
          </div>
          <div className="option-card">
            <span className="option-icon">📊</span>
            <div className="option-title">Real-time Pricing</div>
            <div className="option-description">Live prices from Amazon and other retailers</div>
          </div>
          <div className="option-card">
            <span className="option-icon">🎯</span>
            <div className="option-title">Personalized</div>
            <div className="option-description">Gift suggestions tailored to your specific needs</div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h4>GiftPedia</h4>
            <ul className="footer-links">
              <li><a href="/about">About Us</a></li>
              <li><a href="/how-it-works">How It Works</a></li>
              <li><a href="/privacy">Privacy Policy</a></li>
              <li><a href="/terms">Terms of Service</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Gift Finder</h4>
            <ul className="footer-links">
              <li><a href="/gift-finder/birthday">Birthday Gifts</a></li>
              <li><a href="/gift-finder/anniversary">Anniversary Gifts</a></li>
              <li><a href="/gift-finder/christmas">Christmas Gifts</a></li>
              <li><a href="/gift-finder/valentines">Valentine's Gifts</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Categories</h4>
            <ul className="footer-links">
              <li><a href="/categories/electronics">Electronics</a></li>
              <li><a href="/categories/fashion">Fashion</a></li>
              <li><a href="/categories/home">Home & Kitchen</a></li>
              <li><a href="/categories/sports">Sports & Outdoors</a></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Connect</h4>
            <ul className="footer-links">
              <li><a href="/contact">Contact Us</a></li>
              <li><a href="/blog">Blog</a></li>
              <li><a href="/app">Mobile App</a></li>
              <li><a href="/api">API</a></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 GiftPedia. All rights reserved. Made with ❤️ for better gift-giving.</p>
        </div>
      </footer>
    </div>
  );
};

export default GiftrulyHomePage;
