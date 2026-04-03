#!/usr/bin/env python3
"""
Test API endpoints
"""

import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing API Endpoints")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health Check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test recommendations endpoint
    try:
        request_data = {
            "user_input": "Birthday gift for brother who loves music, budget 2000",
            "max_recommendations": 3
        }
        
        response = requests.post(f"{base_url}/recommendations", json=request_data)
        print(f"✅ Recommendations: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Recommendations: {len(result.get('data', {}).get('recommendations', []))}")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
            
            # Show first recommendation
            recommendations = result.get('data', {}).get('recommendations', [])
            if recommendations:
                first_rec = recommendations[0]
                print(f"   First Recommendation: {first_rec.get('name')} - ₹{first_rec.get('price_inr')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Recommendations Failed: {e}")
    
    # Test categories endpoint
    try:
        response = requests.get(f"{base_url}/categories")
        print(f"✅ Categories: {response.status_code}")
        categories = response.json()
        print(f"   Found {len(categories)} categories")
        for cat in categories[:3]:
            print(f"   - {cat['name']}: {cat['product_count']} products")
    except Exception as e:
        print(f"❌ Categories Failed: {e}")
    
    print("\n🎉 API Testing Complete!")

if __name__ == "__main__":
    test_api()
