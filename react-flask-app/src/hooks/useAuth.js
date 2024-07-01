import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../components/axiosConfig';

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [roles, setRoles] = useState([]);
  const [redirectPath, setRedirectPath] = useState('/');
  const navigate = useNavigate();

  const handleLogin = useCallback(async (email, password) => {
    try {
      const response = await axios.post('/auth/login', { email, password });
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
      console.error('Login failed:', error);
      setIsLoggedIn(false);
    }
  }, [navigate, redirectPath]);

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
    setIsLoggedIn,
    setUsername,
    setToken,
    setRoles,
    setRedirectPath,
  };
};
