import { useState, useEffect } from 'react';
import axios from '../components/axiosConfig'; // Import the Axios configuration

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');

  const handleLogin = async (email, password) => {
    try {
      const response = await axios.post('/auth/login', { email, password });
      setUsername(response.data.logged_in_as);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/auth/logout');
      setIsLoggedIn(false);
      setUsername('');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await axios.get('/auth/status');
        setIsLoggedIn(response.data.loggedIn);
        setUsername(response.data.username || '');
      } catch (error) {
        setIsLoggedIn(false);
        setUsername('');
      }
    };

    checkAuthStatus();
  }, []); // Only run once on mount

  return {
    isLoggedIn,
    username,
    handleLogin,
    handleLogout,
    setIsLoggedIn,
    setUsername
  };
};
