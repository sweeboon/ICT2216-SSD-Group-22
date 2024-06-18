import { useState, useEffect } from 'react';
import axios from 'axios';

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await axios.get('/auth/protected');
        setUsername(response.data.logged_in_as);
        setIsLoggedIn(true);
      } catch (error) {
        console.log('No active session');
      }
    };

    checkSession();
  }, []);

  const getCsrfToken = async () => {
    const response = await axios.get('/auth/csrf-token');
    return response.data.csrf_token;
  };

  const handleLogin = async (email, password) => {
    const csrfToken = await getCsrfToken();
    try {
      const response = await axios.post('/auth/login', { email, password }, {
        headers: { 'X-CSRFToken': csrfToken }
      });
      setUsername(response.data.logged_in_as);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleLogout = async () => {
    const csrfToken = await getCsrfToken();
    try {
      await axios.post('/auth/logout', {}, {
        headers: { 'X-CSRFToken': csrfToken }
      });
      setIsLoggedIn(false);
      setUsername('');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return {
    isLoggedIn,
    username,
    handleLogin,
    handleLogout,
    setIsLoggedIn,
    setUsername
  };
};
