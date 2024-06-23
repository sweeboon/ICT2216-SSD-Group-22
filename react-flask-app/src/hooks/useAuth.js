import { useState, useEffect } from 'react';
import axios from 'axios';

export const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await axios.get('/auth/protected', { withCredentials: true });
        setUsername(response.data.logged_in_as);
        setIsLoggedIn(true);
      } catch (error) {
        console.log('No active session');
      }
    };

    checkSession();
  }, []);

  const handleLogin = async (email, password) => {
    try {
      const response = await axios.post('/auth/login', { email, password }, { withCredentials: true });
      setUsername(response.data.logged_in_as);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/auth/logout', {}, { withCredentials: true });
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
