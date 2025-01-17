import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useSearchParams, useNavigate } from 'react-router-dom';
import '../css/Auth.css';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('Submitting password reset form');
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      console.log('Passwords do not match');
      return;
    }
    try {
      console.log('Sending password reset request');
      const response = await axios.post(`/auth/reset_password`, { token, new_password: newPassword, confirm_password: confirmPassword });
      console.log('Password reset response:', response);
      setMessage(response.data.message);
      setError('');
      setTimeout(() => navigate('/login'), 3000); // Redirect to login page after 3 seconds
    } catch (error) {
      console.error('Error resetting password:', error);
      setError('Error resetting password. Please try again.');
      setMessage('');
    }
  };

  useEffect(() => {
    if (!token) {
      setError('Invalid or expired token.');
      console.log('Invalid or expired token');
    }
  }, [token]);

  if (!token) {
    return <div className="auth-container"><p>{error}</p></div>;
  }

  return (
    <div className='content'>
    <main className="auth-container">
      <h2>Reset Password</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>New Password:</label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Confirm Password:</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit">Reset Password</button>
        {message && <p className="message">{message}</p>}
        {error && <p className="error">{error}</p>}
      </form>
      </main>
      <footer className="footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default ResetPassword;
