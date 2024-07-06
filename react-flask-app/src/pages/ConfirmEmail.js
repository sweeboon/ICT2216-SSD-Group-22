import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import axios from '../components/axiosConfig';
import alcoholImage from '../assets/images/alcohol.png';

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

export default ConfirmEmail;