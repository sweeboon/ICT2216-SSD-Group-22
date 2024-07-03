import axios from 'axios';
import { useEffect } from 'react';

const useTokenRefresh = () => {
  useEffect(() => {
    const refreshToken = async () => {
      try {
        await axios.post('/auth/refresh', {}, { withCredentials: true });
      } catch (error) {
        console.error('Error refreshing token:', error);
      }
    };

    const interval = setInterval(refreshToken, 30 * 60 * 1000); 
    return () => clearInterval(interval);
  }, []);
};

export default useTokenRefresh;
