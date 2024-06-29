import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:5000',
  withCredentials: true,
});

axiosInstance.defaults.withCredentials = true;

axiosInstance.interceptors.request.use(
  config => {
    const token = document.cookie.split('; ').find(row => row.startsWith('XSRF-TOKEN='));
    if (token) {
      config.headers['X-XSRF-TOKEN'] = token.split('=')[1];
    }
    const jwtToken = localStorage.getItem('token');
    if (jwtToken) {
      config.headers['Authorization'] = `Bearer ${jwtToken}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

export default axiosInstance;
