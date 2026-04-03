import React from 'react';

export default function MinimalHomePage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>
        GiftPedia - Minimal Version
      </h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        Find the perfect gift with AI-powered recommendations
      </p>
      
      <div style={{ 
        backgroundColor: 'white', 
        padding: '30px', 
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <h2 style={{ color: '#333', marginBottom: '20px' }}>
          Tell us about the gift you're looking for
        </h2>
        
        <form style={{ marginBottom: '20px' }}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Describe your gift idea
            </label>
            <textarea
              style={{
                width: '100%',
                height: '100px',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '5px',
                fontSize: '16px'
              }}
              defaultValue="Birthday gift for brother who loves music, budget ₹2000"
            />
          </div>
          
          <button
            type="submit"
            style={{
              backgroundColor: '#0070f3',
              color: 'white',
              padding: '12px 24px',
              border: 'none',
              borderRadius: '5px',
              fontSize: '16px',
              cursor: 'pointer',
              width: '100%'
            }}
          >
            Get Gift Recommendations
          </button>
        </form>
      </div>
      
      <div style={{ textAlign: 'center' }}>
        <a 
          href="/results" 
          style={{
            color: '#0070f3',
            textDecoration: 'underline'
          }}
        >
          Or view sample results →
        </a>
      </div>
      
      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
        <h3 style={{ color: '#333', marginBottom: '10px' }}>Test Links:</h3>
        <ul style={{ color: '#666', listStyle: 'none', padding: 0 }}>
          <li><a href="/results" style={{ color: '#0070f3' }}>Results Page</a></li>
          <li><a href="/minimal" style={{ color: '#0070f3' }}>Minimal Test Page</a></li>
          <li><a href="/test" style={{ color: '#0070f3' }}>Test Page</a></li>
        </ul>
      </div>
    </div>
  );
}
