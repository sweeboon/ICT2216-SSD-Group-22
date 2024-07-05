import React, { useState, useEffect } from 'react';
import { useNavigate, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import axios from 'axios';
import '../assets/Auth.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const { isLoggedIn, handleLogin, isOtpRequested } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [resendConfirmation, setResendConfirmation] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(false);
  const [resendCooldownTime, setResendCooldownTime] = useState(0);

  const from = location.state?.from?.pathname || '/';

  useEffect(() => {
    if (resendCooldownTime > 0) {
      const timer = setInterval(() => {
        setResendCooldownTime(resendCooldownTime - 1);
      }, 1000);
      return () => clearInterval(timer);
    } else {
      setResendCooldown(false);
    }
  }, [resendCooldownTime]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await handleLogin(email, password, otp);
      if (response.data.resend_confirmation) {
        setResendConfirmation(true);
      } else {
        setError('');
      }
    } catch (error) {
      if (error.response && error.response.status === 403 && error.response.data.resend_confirmation) {
        setResendConfirmation(true);
      } else {
        if (error.response && error.response.status === 403) {
          setError('Account is locked. Please try again later.');
        } else if (error.response && error.response.status === 400 && error.response.data.message.includes('Confirmation email already sent')) {
          setResendCooldown(true);
          setResendCooldownTime(60);  // Set the cooldown time to 60 seconds
          setError(error.response.data.message);
        } else {
          setError('Invalid credentials or OTP. Please try again.');
        }
      }
    }
  };

  const handleResendConfirmation = async () => {
    try {
      await axios.post('/auth/resend_confirmation_email', { email });
      alert('Confirmation email sent. Please check your email.');
      setResendCooldown(true);
      setResendCooldownTime(60);  // Set the cooldown time to 60 seconds
      setResendConfirmation(false);
    } catch (error) {
      console.error('Error resending confirmation email:', error);
      setError('Failed to resend confirmation email. Please try again.');
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
            disabled={isOtpRequested}
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
        <button type="submit" disabled={resendCooldown}>
          {isOtpRequested ? 'Verify OTP and Login' : 'Request OTP'}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
      {resendConfirmation && (
        <div>
          <p>Your account is not confirmed. Do you want to resend the confirmation email?</p>
          <button onClick={handleResendConfirmation} disabled={resendCooldown}>
            Resend Confirmation Email
          </button>
        </div>
      )}
      {resendCooldown && <p>Please wait {resendCooldownTime} seconds before requesting a new confirmation email.</p>}
    </div>
  );
};

export default Login;
