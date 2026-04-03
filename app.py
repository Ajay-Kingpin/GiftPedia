"""
GiftPedia AI-Powered Gift Discovery Platform
Streamlit Cloud Deployment
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="GiftPedia - AI Gift Discovery",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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
    
    .step-indicator {
        background: #6366f1;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        margin-bottom: 1rem;
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
        'budget': ''
    }
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

# Header
st.markdown("""
<div class="main-header">
    <h1>🎁 GiftPedia</h1>
    <h2>AI-Powered Gift Discovery Platform</h2>
    <p>Revolutionary platform that combines artificial intelligence with personalized recommendations</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🚀 Platform Features")
    st.markdown("""
    🤖 **AI-Powered Recommendations**
    Advanced machine learning algorithms
    
    💰 **Real-Time Pricing**
    Live market prices across retailers
    
    🔗 **Affiliate Integration**
    Automatic monetization
    
    📱 **Mobile Responsive**
    Works on all devices
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
    • **25%** Annual growth
    • **65%** Prefer AI recommendations
    """)

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
        interests = st.text_input("Interests & Hobbies", placeholder="e.g., music, cooking, reading", key="interests")
        additional_info = st.text_area("Additional Details", placeholder="Tell us more about their personality...", key="additional_info")
    
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
                st.error("Please fill in all required fields")

def get_recommendations():
    """Generate AI-powered recommendations"""
    st.markdown('<div class="step-indicator">Step 4: AI Recommendations</div>', unsafe_allow_html=True)
    
    with st.spinner("🤖 AI is finding perfect gifts..."):
        time.sleep(2)  # Simulate API call
        
        # Generate mock recommendations
        products = [
            {
                "name": "Wireless Bluetooth Headphones",
                "brand": "Sony",
                "price": 4999,
                "currency": "INR",
                "availability": "In Stock",
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
                "description": "Professional stainless steel knife set",
                "features": ["Stainless Steel", "Professional", "Sharp", "Cooking"],
                "affiliate_url": "https://amazon.in/dp/B08N5M8X5K"
            },
            {
                "name": "Silk Scarf with Floral Pattern",
                "brand": "FabIndia",
                "price": 1299,
                "currency": "INR",
                "availability": "In Stock",
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
                "description": "WiFi security camera with night vision",
                "features": ["WiFi", "Night Vision", "Mobile App", "Security"],
                "affiliate_url": "https://amazon.in/dp/B08N5M8X5K"
            }
        ]
        
        st.session_state.recommendations = products
        st.session_state.current_step = 4
        st.rerun()

def step_4_results():
    st.markdown('<div class="step-indicator">Step 4: Your Personalized Recommendations</div>', unsafe_allow_html=True)
    
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
                    <p><span class="availability in-stock">{product['availability']}</span></p>
                    <p>{product['description']}</p>
                    <p><strong>Features:</strong> {', '.join(product['features'][:3])}</p>
                    <a href="{product['affiliate_url']}" target="_blank">
                        <button style="background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); color: white; padding: 0.5rem 1rem; border: none; border-radius: 5px; cursor: pointer; width: 100%;">
                            🛒 Shop Now
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Analytics section
    st.markdown("### 📊 Platform Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", "50,000+", "↑ 25%")
    with col2:
        st.metric("Success Rate", "95%", "↑ 5%")
    with col3:
        st.metric("Avg. Response", "0.2s", "↓ 10%")
    with col4:
        st.metric("Revenue", "₹25L", "↑ 30%")
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 User Growth")
        chart_data = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
            "Users": [10000, 15000, 22000, 35000, 50000]
        })
        fig = px.line(chart_data, x="Month", y="Users", title="User Growth Trend")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 💰 Revenue Trends")
        revenue_data = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May"],
            "Revenue": [500000, 750000, 1200000, 1800000, 2500000]
        })
        fig = px.line(revenue_data, x="Month", y="Revenue", title="Revenue Growth")
        st.plotly_chart(fig, use_container_width=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Start Over", key="start_over", use_container_width=True):
            st.session_state.current_step = 1
            st.session_state.gift_request = {
                'occasion': '',
                'recipient': '',
                'age': '',
                'interests': '',
                'budget': ''
            }
            st.session_state.recommendations = []
            st.rerun()
    
    with col2:
        if st.button("📊 Full Analytics", key="full_analytics", use_container_width=True):
            st.success("Analytics dashboard coming soon!")

# Progress indicator
progress = st.session_state.current_step / 4
st.progress(progress)
st.caption(f"Step {st.session_state.current_step} of 4")

# Main app logic
def main():
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
    <p>🚀 Stakeholder Demo | Built with Advanced AI Technology</p>
    <p>© 2024 GiftPedia. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
