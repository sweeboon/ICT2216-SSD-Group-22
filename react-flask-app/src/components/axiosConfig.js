import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'https://forteam22ict.xyz',//baseURL: 'http://localhost:5000',//baseURL: 'https://forteam22ict.xyz', // //for live server change to need to use this line if testing on local, change back to 127.0.0.1
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
