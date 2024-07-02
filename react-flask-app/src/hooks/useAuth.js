import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../components/axiosConfig';

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [roles, setRoles] = useState([]);
  const [redirectPath, setRedirectPath] = useState('/');
  const [isOtpRequested, setIsOtpRequested] = useState(false);  // Track OTP request status

  const navigate = useNavigate();

  const initiateLogin = useCallback(async (email, password) => {
    try {
      const response = await axios.post('/auth/initiate_login', { email, password });
      setIsOtpRequested(true);
      return response.data;
    } catch (error) {
      setIsOtpRequested(false);
      throw error;
    }
  }, []);

  const verifyOtpAndLogin = useCallback(async (email, otp) => {
    try {
      const response = await axios.post('/auth/verify_otp_and_login', { email, otp });
      const jwtToken = response.data.token;
      const loggedUsername = response.data.username;
      const userRoles = response.data.roles;

      setToken(jwtToken);
      localStorage.setItem('token', jwtToken);
      setUsername(loggedUsername);
      setRoles(userRoles);
      setIsLoggedIn(true);
      console.log('Login successful, isLoggedIn:', true);
      navigate(redirectPath);
    } catch (error) {
      setIsLoggedIn(false);
      throw error;
    }
  }, [navigate, redirectPath]);

  const handleLogin = useCallback(async (email, password, otp) => {
    if (isOtpRequested) {
      await verifyOtpAndLogin(email, otp);
    } else {
      await initiateLogin(email, password);
    }
  }, [initiateLogin, verifyOtpAndLogin, isOtpRequested]);

  const handleLogout = useCallback(async () => {
    try {
      await axios.post('/auth/logout');
      setIsLoggedIn(false);
      setUsername('');
      setToken('');
      setRoles([]);
      localStorage.removeItem('token');
      document.cookie = 'XSRF-TOKEN=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
      document.cookie = 'session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
      console.log('Logout successful, isLoggedIn:', false);
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  }, [navigate]);

  const checkAuthStatus = useCallback(async () => {
    try {
      const response = await axios.get('/auth/status');
      setIsLoggedIn(response.data.loggedIn);
      setUsername(response.data.username || '');
      setRoles(response.data.roles || []);
      console.log('Auth status checked, isLoggedIn:', response.data.loggedIn);
    } catch (error) {
      console.error('Auth status check failed:', error);
      setIsLoggedIn(false);
      setUsername('');
      setRoles([]);
    }
  }, []);

  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  return {
    isLoggedIn,
    username,
    token,
    roles,
    handleLogin,
    handleLogout,
    checkAuthStatus,
    isOtpRequested,
    setIsLoggedIn,
    setUsername,
    setToken,
    setRoles,
    setRedirectPath,
  };
};
