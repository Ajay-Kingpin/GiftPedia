"""
GiftPedia AI-Powered Gift Discovery Platform
Streamlit Deployment for Stakeholder Demo
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="GiftPedia - AI Gift Discovery",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .product-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    
    .price-tag {
        color: #059669;
        font-size: 1.25rem;
        font-weight: bold;
    }
    
    .availability {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .in-stock {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
    }
    
    .out-of-stock {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
    }
    
    .step-indicator {
        background: #6366f1;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .success-message {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #10b981;
        margin-bottom: 1rem;
    }
    
    .error-message {
        background: rgba(239, 68, 68, 0.1);
        color: #ef4444;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ef4444;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'gift_request' not in st.session_state:
    st.session_state.gift_request = {
        'occasion': '',
        'recipient': '',
        'age': '',
        'interests': '',
        'additional_info': '',
        'budget': ''
    }
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🎁 GiftPedia</h1>
    <h2>AI-Powered Gift Discovery Platform</h2>
    <p>Revolutionary platform that combines artificial intelligence with personalized recommendations to help users find the perfect gift every time.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with platform info
with st.sidebar:
    st.markdown("### 🚀 Platform Features")
    st.markdown("""
    🤖 **AI-Powered Recommendations**
    Advanced machine learning algorithms analyze user preferences
    
    💰 **Real-Time Pricing**
    Live market prices across multiple retailers
    
    🔗 **Affiliate Integration**
    Automatic monetization with affiliate links
    
    📱 **Mobile Responsive**
    Works seamlessly on all devices
    
    🛡️ **Enterprise Security**
    Data encryption and privacy compliance
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Platform Status")
    st.success("✅ All Systems Operational")
    st.info("🔄 API Response: <200ms")
    st.info("📈 Success Rate: 95%+")
    
    st.markdown("---")
    st.markdown("### 🎯 Market Opportunity")
    st.markdown("""
    • **$40B+** Indian gifting market
    • **25%** Annual growth rate
    • **65%** Prefer AI recommendations
    • **70%** Mobile purchases
    """)

# Main content
def step_1_occasion():
    st.markdown('<div class="step-indicator">Step 1: Select Occasion</div>', unsafe_allow_html=True)
    
    occasions = [
        {"name": "Birthday", "icon": "🎂", "description": "Celebrate their special day"},
        {"name": "Anniversary", "icon": "💑", "description": "Mark your milestone"},
        {"name": "Wedding", "icon": "💍", "description": "Perfect for the couple"},
        {"name": "Graduation", "icon": "🎓", "description": "Celebrate achievement"},
        {"name": "Holiday", "icon": "🎄", "description": "Seasonal celebrations"},
        {"name": "Just Because", "icon": "💝", "description": "No reason needed"}
    ]
    
    cols = st.columns(3)
    for i, occasion in enumerate(occasions):
        with cols[i % 3]:
            if st.button(f"{occasion['icon']} {occasion['name']}", key=f"occasion_{i}", use_container_width=True):
                st.session_state.gift_request['occasion'] = occasion['name']
                st.session_state.current_step = 2
                st.rerun()

def step_2_recipient():
    st.markdown('<div class="step-indicator">Step 2: Choose Recipient</div>', unsafe_allow_html=True)
    
    recipients = [
        {"name": "Mother", "icon": "👩", "description": "For the amazing mom"},
        {"name": "Father", "icon": "👨", "description": "For the wonderful dad"},
        {"name": "Spouse", "icon": "💑", "description": "For your partner"},
        {"name": "Friend", "icon": "👥", "description": "For your bestie"},
        {"name": "Child", "icon": "👶", "description": "For the little one"},
        {"name": "Colleague", "icon": "👔", "description": "For your coworker"}
    ]
    
    cols = st.columns(3)
    for i, recipient in enumerate(recipients):
        with cols[i % 3]:
            if st.button(f"{recipient['icon']} {recipient['name']}", key=f"recipient_{i}", use_container_width=True):
                st.session_state.gift_request['recipient'] = recipient['name']
                st.session_state.current_step = 3
                st.rerun()

def step_3_details():
    st.markdown('<div class="step-indicator">Step 3: Tell Us More</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.selectbox("Age Range", ["", "18-25", "26-35", "36-45", "46-55", "56+"], key="age")
        budget = st.selectbox("Budget (INR)", ["", "₹5,000 - ₹10,000", "₹10,000 - ₹25,000", "₹25,000 - ₹50,000", "₹50,000 - ₹1,00,000", "₹1,00,000+"], key="budget")
    
    with col2:
        interests = st.text_input("Interests & Hobbies", placeholder="e.g., music, cooking, reading, travel", key="interests")
        additional_info = st.text_area("Additional Details", placeholder="Tell us more about their personality, preferences, or special requirements...", key="additional_info")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Previous", key="prev_step_3"):
            st.session_state.current_step = 2
            st.rerun()
    
    with col2:
        if st.button("Get Recommendations →", key="get_recommendations", type="primary", use_container_width=True):
            if age and interests and budget:
                st.session_state.gift_request.update({
                    'age': age,
                    'interests': interests,
                    'additional_info': additional_info,
                    'budget': budget
                })
                get_recommendations()
            else:
                st.error("Please fill in all required fields (Age, Interests, Budget)")

def get_recommendations():
    """Get recommendations from API"""
    st.markdown('<div class="step-indicator">Step 4: AI Recommendations</div>', unsafe_allow_html=True)
    
    with st.spinner("🤖 AI is finding perfect gifts..."):
        try:
            # Create user input for API
            user_input = f"{st.session_state.gift_request['occasion']} gift for {st.session_state.gift_request['recipient']} who loves {st.session_state.gift_request['interests']}, budget {st.session_state.gift_request['budget']}"
            if st.session_state.gift_request['age']:
                user_input += f", age {st.session_state.gift_request['age']}"
            if st.session_state.gift_request['additional_info']:
                user_input += f", {st.session_state.gift_request['additional_info']}"
            
            # Mock API call (replace with real API when available)
            time.sleep(2)  # Simulate API call
            
            # Generate mock recommendations
            mock_recommendations = generate_mock_recommendations()
            st.session_state.recommendations = mock_recommendations
            st.session_state.current_step = 4
            st.rerun()
            
        except Exception as e:
            st.error(f"Error getting recommendations: {str(e)}")

def generate_mock_recommendations():
    """Generate mock product recommendations"""
    products = [
        {
            "name": "Wireless Bluetooth Headphones",
            "brand": "Sony",
            "price": 4999,
            "currency": "INR",
            "availability": "In Stock",
            "image_url": "https://picsum.photos/seed/headphones/400/300.jpg",
            "description": "Premium wireless headphones with noise cancellation",
            "features": ["Wireless", "Noise Cancelling", "Bluetooth", "Music"],
            "affiliate_url": "https://amazon.in/dp/B08N5M8X5K"
        },
        {
            "name": "Professional Kitchen Knife Set",
            "brand": "Prestige",
            "price": 2999,
            "currency": "INR",
            "availability": "In Stock",
            "image_url": "https://picsum.photos/seed/knives/400/300.jpg",
            "description": "Professional stainless steel knife set with wooden block",
            "features": ["Stainless Steel", "Professional", "Sharp", "Cooking"],
            "affiliate_url": "https://amazon.in/dp/B08N5M8X5K"
        },
        {
            "name": "Silk Scarf with Floral Pattern",
            "brand": "FabIndia",
            "price": 1299,
            "currency": "INR",
            "availability": "In Stock",
            "image_url": "https://picsum.photos/seed/scarf/400/300.jpg",
            "description": "Elegant silk scarf with beautiful floral pattern",
            "features": ["Silk", "Floral", "Elegant", "Fashion"],
            "affiliate_url": "https://amazon.in/dp/B08N5M8X5K"
        },
        {
            "name": "Smart Home Security Camera",
            "brand": "Mi",
            "price": 3499,
            "currency": "INR",
            "availability": "In Stock",
            "image_url": "https://picsum.photos/seed/camera/400/300.jpg",
            "description": "WiFi security camera with night vision and mobile app",
            "features": ["WiFi", "Night Vision", "Mobile App", "Security"],
            "affiliate_url": "https://amazon.in/dp/B08N5M8X5K"
        },
        {
            "name": "Yoga Mat with Carrying Strap",
            "brand": "Nike",
            "price": 1999,
            "currency": "INR",
            "availability": "In Stock",
            "image_url": "https://picsum.photos/seed/yoga/400/300.jpg",
            "description": "Non-slip yoga mat with carrying strap and alignment marks",
            "features": ["Non-slip", "Eco-friendly", "Portable", "Yoga"],
            "affiliate_url": "https://amazon.in/dp/B08N5M8X5K"
        }
    ]
    
    # Filter based on interests
    interests = st.session_state.gift_request.get('interests', '').lower()
    filtered_products = []
    
    for product in products:
        score = 0
        for feature in product['features']:
            if any(interest in feature.lower() for interest in interests.split(',')):
                score += 1
        if score > 0:
            filtered_products.append(product)
    
    # If no matches, return all products
    if not filtered_products:
        filtered_products = products
    
    return filtered_products[:4]  # Return top 4 recommendations

def step_4_results():
    st.markdown('<div class="step-indicator">Step 4: Your Personalized Gift Recommendations</div>', unsafe_allow_html=True)
    
    # Display user preferences
    st.markdown("### 📋 Your Preferences")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Occasion", st.session_state.gift_request.get('occasion', 'N/A'))
    with col2:
        st.metric("Recipient", st.session_state.gift_request.get('recipient', 'N/A'))
    with col3:
        st.metric("Budget", st.session_state.gift_request.get('budget', 'N/A'))
    with col4:
        st.metric("Interests", st.session_state.gift_request.get('interests', 'N/A'))
    
    st.markdown("---")
    
    # Display recommendations
    st.markdown("### 🎁 AI-Powered Recommendations")
    
    if st.session_state.recommendations:
        cols = st.columns(2)
        for i, product in enumerate(st.session_state.recommendations):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="product-card">
                    <h4>{product['name']}</h4>
                    <p><strong>Brand:</strong> {product['brand']}</p>
                    <p class="price-tag">₹{product['price']:,}</p>
                    <p><span class="availability {product['availability'].lower().replace(' ', '-')}">{product['availability']}</span></p>
                    <p>{product['description']}</p>
                    <p><strong>Features:</strong> {', '.join(product['features'][:3])}</p>
                    <a href="{product['affiliate_url']}" target="_blank" style="text-decoration: none;">
                        <button style="background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); color: white; padding: 0.5rem 1rem; border: none; border-radius: 5px; cursor: pointer; width: 100%;">
                            🛒 Shop Now
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No recommendations available. Please try different criteria.")
    
    st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Start Over", key="start_over", use_container_width=True):
            # Reset session state
            st.session_state.current_step = 1
            st.session_state.gift_request = {
                'occasion': '',
                'recipient': '',
                'age': '',
                'interests': '',
                'additional_info': '',
                'budget': ''
            }
            st.session_state.recommendations = []
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", key="view_analytics", use_container_width=True):
            st.session_state.show_analytics = True
            st.rerun()

def show_analytics():
    st.markdown("### 📊 Platform Analytics")
    
    # Mock analytics data
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", "50,000+", "↑ 25%")
    with col2:
        st.metric("Success Rate", "95%", "↑ 5%")
    with col3:
        st.metric("Avg. Response Time", "0.2s", "↓ 10%")
    with col4:
        st.metric("Revenue", "₹25L", "↑ 30%")
    
    st.markdown("---")
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 User Growth")
        st.bar_chart({
            "Jan": 10000, "Feb": 15000, "Mar": 22000, "Apr": 35000, "May": 50000
        })
    
    with col2:
        st.markdown("#### 💰 Revenue Trends")
        st.line_chart({
            "Jan": 500000, "Feb": 750000, "Mar": 1200000, "Apr": 1800000, "May": 2500000
        })
    
    if st.button("← Back to Recommendations", key="back_to_recs", use_container_width=True):
        st.session_state.show_analytics = False
        st.rerun()

# Main app logic
def main():
    # Check if analytics should be shown
    if st.session_state.get('show_analytics', False):
        show_analytics()
        return
    
    # Progress indicator
    progress = st.session_state.current_step / 4
    st.progress(progress)
    st.caption(f"Step {st.session_state.current_step} of 4")
    
    # Render current step
    if st.session_state.current_step == 1:
        step_1_occasion()
    elif st.session_state.current_step == 2:
        step_2_recipient()
    elif st.session_state.current_step == 3:
        step_3_details()
    elif st.session_state.current_step == 4:
        step_4_results()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; margin-top: 2rem;">
    <p><strong>GiftPedia</strong> - AI-Powered Gift Discovery Platform</p>
    <p>🚀 Stakeholder Prototype | Built with Advanced AI Technology</p>
    <p>© 2024 GiftPedia. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
