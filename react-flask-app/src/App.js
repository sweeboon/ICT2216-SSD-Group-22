import React from 'react';
import { Route, Routes, Link } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import ProductComponent from './components/ProductComponent';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import HomePage from './pages/HomePage';
import { useAuth } from './hooks/useAuth';
import ConfirmEmail from './pages/ConfirmEmail';
import ConfirmationResult from './pages/ConfirmationResult';

const App = () => {
  const { isLoggedIn } = useAuth();

  return (
    <div>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/products">Manage Products</Link>
        {isLoggedIn && <Link to="/profile">Profile</Link>}
      </nav>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/products" element={<ProductComponent />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/confirm" element={<ConfirmEmail />} />
        <Route path="/confirm-result" element={<ConfirmationResult />} />
      </Routes>
    </div>
  );
};

export default App;
