import React from 'react';

export default function MinimalResultsPage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>
        Your Gift Recommendations
      </h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>
        Found 2 personalized recommendations based on your request.
      </p>
      
      <div style={{ display: 'grid', gap: '20px', marginBottom: '30px' }}>
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '10px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        }}>
          <div style={{ backgroundColor: '#f0f0f0', height: '200px', borderRadius: '5px', marginBottom: '15px' }}></div>
          <h3 style={{ color: '#333', marginBottom: '10px' }}>Fender Guitar Strap</h3>
          <p style={{ color: '#666', marginBottom: '10px' }}>Music & Instruments • Fender</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <span style={{ fontSize: '24px', fontWeight: 'bold', color: '#0070f3' }}>₹1899</span>
            <span style={{ color: '#666' }}>Score: 80%</span>
          </div>
          <button style={{
            backgroundColor: '#0070f3',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            width: '100%'
          }}>
            View Details
          </button>
        </div>
        
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '10px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        }}>
          <div style={{ backgroundColor: '#f0f0f0', height: '200px', borderRadius: '5px', marginBottom: '15px' }}></div>
          <h3 style={{ color: '#333', marginBottom: '10px' }}>Wireless Headphones</h3>
          <p style={{ color: '#666', marginBottom: '10px' }}>Electronics • Sony</p>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <span style={{ fontSize: '24px', fontWeight: 'bold', color: '#0070f3' }}>₹2499</span>
            <span style={{ color: '#666' }}>Score: 70%</span>
          </div>
          <button style={{
            backgroundColor: '#0070f3',
            color: 'white',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            width: '100%'
          }}>
            View Details
          </button>
        </div>
      </div>
      
      <div style={{ 
        backgroundColor: '#e3f2fd', 
        padding: '20px', 
        borderRadius: '10px',
        marginBottom: '30px'
      }}>
        <h2 style={{ color: '#1976d2', marginBottom: '10px' }}>Summary</h2>
        <p style={{ color: '#1976d2' }}>
          Found 2 personalized gift recommendations based on your request. These options match the recipient's interests in music and fit within your budget.
        </p>
      </div>
      
      <div style={{ textAlign: 'center' }}>
        <button
          onClick={() => window.location.href = '/'}
          style={{
            backgroundColor: '#0070f3',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '5px',
            fontSize: '16px',
            cursor: 'pointer'
          }}
        >
          Get More Recommendations
        </button>
      </div>
      
      <div style={{ marginTop: '40px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
        <h3 style={{ color: '#333', marginBottom: '10px' }}>Test Links:</h3>
        <ul style={{ color: '#666', listStyle: 'none', padding: 0 }}>
          <li><a href="/" style={{ color: '#0070f3' }}>Home Page</a></li>
          <li><a href="/minimal" style={{ color: '#0070f3' }}>Minimal Test Page</a></li>
          <li><a href="/test" style={{ color: '#0070f3' }}>Test Page</a></li>
        </ul>
      </div>
    </div>
  );
}
