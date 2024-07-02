import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from '../components/axiosConfig';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [roles, setRoles] = useState([]);

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await axios.get('/auth/status');
        setIsLoggedIn(response.data.loggedIn);
        setUsername(response.data.username || '');
        setRoles(response.data.roles || []);
      } catch (error) {
        setIsLoggedIn(false);
        setUsername('');
        setRoles([]);
      }
    };
    checkAuthStatus();
  }, []);

  const handleLogin = async (email, password) => {
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
    } catch (error) {
      setIsLoggedIn(false);
      throw error; // Re-throw to handle in the component
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post('/auth/logout');
      setIsLoggedIn(false);
      setUsername('');
      setToken('');
      setRoles([]);
      localStorage.removeItem('token');
      document.cookie = 'XSRF-TOKEN=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
      document.cookie = 'session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
      window.location.reload(); // Force a full reload to clear all states
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, username, token, roles, handleLogin, handleLogout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
