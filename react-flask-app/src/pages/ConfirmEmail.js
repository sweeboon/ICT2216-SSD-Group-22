import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';

const ConfirmEmail = () => {
  const query = new URLSearchParams(useLocation().search);
  const token = query.get('token');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const confirmEmail = async () => {
      try {
        const response = await axios.get('/auth/confirm', {
          params: { token },
        });
        setMessage(response.data.message);
        setError('');
      } catch (error) {
        setError('Invalid or expired confirmation link.');
        setMessage('');
      }
    };
    confirmEmail();
  }, [token]);

  return (
    <div className="confirmation-container">
      {message && <h2>{message}</h2>}
      {error && <h2>{error}</h2>}
    </div>
  );
};

export default ConfirmEmail;
