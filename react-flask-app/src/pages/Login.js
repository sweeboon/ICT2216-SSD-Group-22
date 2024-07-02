import React, { useState } from 'react';
import { useNavigate, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import '../assets/Auth.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');  // For success messages
  const { isLoggedIn, handleLogin, isOtpRequested } = useAuth();  // Use new hooks
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await handleLogin(email, password, otp);
      setSuccess('OTP sent to your email.');
      setError('');
    } catch (error) {
      setError('Login failed. Please check your email, password, and OTP.');
      setSuccess('');
    }
  };

  if (isLoggedIn) {
    return <Navigate to={from} replace />;
  }

  return (
    <div className="auth-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isOtpRequested}  // Disable after OTP is requested
          />
        </div>
        {isOtpRequested && (
          <div>
            <label>OTP:</label>
            <input
              type="text"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              required
            />
          </div>
        )}
        <button type="submit">
          {isOtpRequested ? 'Verify OTP and Login' : 'Request OTP'}
        </button>
        {error && <p className="error">{error}</p>}  
        {success && <p className="success">{success}</p>} 
      </form>
    </div>
  );
};

export default Login;
