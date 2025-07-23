import React from 'react';

export default function TestForm() {
  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>Test Form</h1>
      <p>This is a test to see if the routing is working.</p>
      <div style={{ background: 'lightblue', padding: '1rem', margin: '1rem' }}>
        <h2>Form Test</h2>
        <input type="text" placeholder="Test input" />
        <button>Test Button</button>
      </div>
    </div>
  );
} 