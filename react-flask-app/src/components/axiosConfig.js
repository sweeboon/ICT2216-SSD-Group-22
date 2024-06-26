import axios from 'axios';

axios.defaults.withCredentials = true;

axios.interceptors.request.use(
  config => {
    const token = document.cookie.split('; ').find(row => row.startsWith('XSRF-TOKEN='));
    if (token) {
      config.headers['X-XSRF-TOKEN'] = token.split('=')[1];
    }
    return config;
  },
  error => Promise.reject(error)
);

export default axios;