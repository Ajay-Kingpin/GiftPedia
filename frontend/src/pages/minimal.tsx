import React from 'react';

export default function MinimalPage() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ color: '#333', marginBottom: '20px' }}>
        Minimal Test Page
      </h1>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        If you can see this page, Next.js is working correctly.
      </p>
      <div style={{ 
        padding: '10px', 
        backgroundColor: '#f0f0f0', 
        borderRadius: '5px',
        marginBottom: '20px'
      }}>
        <p>✅ Next.js routing works</p>
        <p>✅ Page compilation successful</p>
        <p>✅ No missing components</p>
      </div>
      <a 
        href="/" 
        style={{
          display: 'inline-block',
          padding: '10px 20px',
          backgroundColor: '#0070f3',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '5px'
        }}
      >
        Back to Home
      </a>
    </div>
  );
}
