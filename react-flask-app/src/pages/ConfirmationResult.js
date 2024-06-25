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
    <div className="confirmation-container">
      <h2>{message}</h2>
    </div>
  );
};

export default ConfirmationResult;
