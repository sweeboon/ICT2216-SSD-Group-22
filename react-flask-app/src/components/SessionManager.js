import React, { useEffect } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

const SessionManager = ({ setSsid }) => {
  const saveSessionToLocalStorage = (token, ssid) => {
    localStorage.setItem('session_token', token);
    localStorage.setItem('session_ssid', ssid);
  };

  const getSessionTokenFromLocalStorage = () => {
    return localStorage.getItem('session_token');
  };

  const getSessionSsidFromLocalStorage = () => {
    return localStorage.getItem('session_ssid');
  };

  useEffect(() => {
    const checkSession = async (token) => {
      try {
        const response = await axios.get('/auth/sessions', {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSsid(response.data.ssid);
        console.log('Session exists and is valid:', response.data.ssid);
      } catch (error) {
        if (error.response && error.response.status === 404) {
          createSession();
        } else {
          console.error('Error checking session:', error);
          createSession();
        }
      }
    };

    const createSession = async () => {
      try {
        const response = await axios.post('/auth/sessions');
        const { token, ssid } = response.data;
        saveSessionToLocalStorage(token, ssid);
        setSsid(ssid);
        console.log('New session created:', ssid);
      } catch (error) {
        console.error('Error creating session:', error);
      }
    };

    const storedToken = getSessionTokenFromLocalStorage();
    const storedSsid = getSessionSsidFromLocalStorage();
    if (storedToken && storedSsid) {
      checkSession(storedToken);
    } else {
      createSession();
    }
  }, [setSsid]);

  return null;
};

SessionManager.propTypes = {
  setSsid: PropTypes.func.isRequired,
};

export default SessionManager;
