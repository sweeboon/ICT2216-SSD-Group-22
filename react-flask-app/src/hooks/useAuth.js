import { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');

  const handleLogin = async (email, password) => {
    try {
      const response = await axios.post('/auth/login', { email, password });
      console.log('Login response:', response.data);

      const jwtToken = response.data.token;
      const loggedUsername = response.data.logged_in_as;

      setToken(jwtToken);
      localStorage.setItem('token', jwtToken);
      setUsername(loggedUsername);

      setIsLoggedIn(true);
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoggedIn(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/auth/logout');
      setIsLoggedIn(false);
      setUsername('');
      setToken('');
      localStorage.removeItem('token');

      // Clear cookies
      document.cookie = 'XSRF-TOKEN=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
      document.cookie = 'session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('/auth/status');
      setIsLoggedIn(response.data.loggedIn);
      setUsername(response.data.username || '');
    } catch (error) {
      console.error('Auth status check failed:', error);
      setIsLoggedIn(false);
      setUsername('');
    }
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  useEffect(() => {
    console.log('isLoggedIn state changed:', isLoggedIn);
  }, [isLoggedIn]);

  return {
    isLoggedIn,
    username,
    token,
    handleLogin,
    handleLogout,
    checkAuthStatus,
    setIsLoggedIn,
    setUsername,
    setToken
  };
};
