import React, {useState} from 'react';
import { Route, Routes, Link } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import Login from './pages/Login';
import Register from './pages/Register';
import HomePage from './pages/HomePage';
import ConfirmEmail from './pages/ConfirmEmail';
import ConfirmationResult from './pages/ConfirmationResult';
import Profile from './pages/Profile';

import ProductComponent from './components/ProductComponent';
import SessionManager from './components/SessionManager';
import LandingPage from './pages/LandingPage';
import Cart from './pages/cart';

const App = () => {
  const { isLoggedIn,token } = useAuth();
  const [ssid, setSsid] = useState(null);

  const referer = document.referrer;

  return (
    <div>
      <p>Current Session ID: {ssid}</p>
      <SessionManager setSsid={setSsid}/>
      <nav>
        <Link to="/landing">Home</Link>
        <Link to="/products">Manage Products</Link>
        <Link to="/cart">Cart</Link>
        {isLoggedIn && <Link to="/profile">Profile</Link>}
      </nav>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/confirm" element={<ConfirmEmail />} />
        <Route path="/confirm-result" element={<ConfirmationResult />} />

        <Route path="/landing" element={<LandingPage />} />
        <Route path="/products" element={<ProductComponent />} />
        <Route path="/cart" element={<Cart />} />
      </Routes>
    </div>
  );
};

export default App;
