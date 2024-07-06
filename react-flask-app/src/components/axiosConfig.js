import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'process.env.REACT_APP_API_BASE_URL',
  withCredentials: true,
});

axiosInstance.defaults.withCredentials = true;

axiosInstance.interceptors.request.use(
  config => {
    const csrfToken = document.cookie.split('; ').find(row => row.startsWith('XSRF-TOKEN='));
    if (csrfToken) {
      config.headers['X-XSRF-TOKEN'] = csrfToken.split('=')[1];
    }
    const jwtToken = document.cookie.split('; ').find(row => row.startsWith('token='));
    if (jwtToken) {
      config.headers['Authorization'] = `Bearer ${jwtToken.split('=')[1]}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

export default axiosInstance;
