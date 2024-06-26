import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from '../components/axiosConfig';

const ConfirmEmail = () => {
  const query = new URLSearchParams(useLocation().search);
  const token = query.get('token');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const confirmEmail = async () => {
      try {
        const response = await axios.get(`/auth/confirm/${token}`);
        setMessage(response.data.message);
        setError('');
        navigate(`/confirmation-result?status=success`);
      } catch (error) {
        setError('Invalid or expired confirmation link.');
        setMessage('');
        navigate(`/confirmation-result?status=invalid`);
      }
    };
    confirmEmail();
  }, [token, navigate]);

  return (
    <div className="confirmation-container">
      {message && <h2>{message}</h2>}
      {error && <h2>{error}</h2>}
    </div>
  );
};

export default ConfirmEmail;
