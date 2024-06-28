import React from 'react';
import ReactDOM from 'react-dom/client';
import './css/index.css';
import HomePage from './pages/HomePage';
import './components/axiosConfig'; // Ensure Axios configuration is imported

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);