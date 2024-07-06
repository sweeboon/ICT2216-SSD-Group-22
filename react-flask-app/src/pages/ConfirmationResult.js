import React from 'react';
import { useLocation } from 'react-router-dom';

const ConfirmationResult = () => {
  const query = new URLSearchParams(useLocation().search);
  const status = query.get('status');

  let message;
  switch (status) {
    case 'success':
      message = 'Your email has been successfully confirmed!';
      break;
    case 'expired':
      message = 'The confirmation link has expired.';
      break;
    case 'invalid':
    default:
      message = 'The confirmation link is invalid or has expired.';
      break;
  }

  return (
    <div className="confirmation-container"
    style={{
    top: '100px',
    left: '0',
    width: '100%',
    height: '81%',
    backgroundImage: `url(${alcoholImage})`,    backgroundSize: 'cover',
    backgroundPosition: 'center',
    position: 'absolute'
    }}>
      <h2
        style={{
          color: '#333',
          fontSize: '24px',
          textAlign: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          padding: '20px',
          boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)'
        }}
      >{message}</h2>
      <footer className="footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default ConfirmationResult;
