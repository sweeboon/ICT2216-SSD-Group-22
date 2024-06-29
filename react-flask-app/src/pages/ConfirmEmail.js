import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from '../components/axiosConfig';

const ConfirmEmail = () => {
  const query = new URLSearchParams(useLocation().search);
  const token = query.get('token');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const confirmEmail = async () => {
      try {
        const response = await axios.get('/auth/confirm', {
          params: { token }
        });
        setMessage(response.data.message);
      } catch (error) {
        setMessage('Invalid or expired confirmation link.');
      }
    };
    confirmEmail();
  }, [token]);

  return (
    <div className="confirmation-container">
      <h2>{message}</h2>
    </div>
  );
};

export default ConfirmEmail;