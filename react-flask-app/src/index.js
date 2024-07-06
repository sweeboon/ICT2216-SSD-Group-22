import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import App from './App';
import './css/index.css';
import useTokenRefresh from './hooks/useTokenRefresh';  

const container = document.getElementById('root');
const root = createRoot(container);

const Root = () => {
  useTokenRefresh();  

  return (
    <Router>
      <AuthProvider>
        <App />
      </AuthProvider>
    </Router>
  );
};

root.render(<Root />);