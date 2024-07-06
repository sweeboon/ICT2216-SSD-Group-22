import React from 'react';
import { Route, Routes, Navigate, useLocation } from 'react-router-dom';
import Cart from './pages/Cart';
import PaymentPage from './pages/PaymentPage';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import LandingPage from './pages/LandingPage';
import ConfirmEmail from './pages/ConfirmEmail';
import ConfirmationResult from './pages/ConfirmEmail';
import OrdersPage from './pages/OrdersPage';
import ProductComponent from './components/ProductComponent';
import { useAuth } from './hooks/useAuth';
import Navbar from './pages/Navbar';
import ManageOrders from './pages/ManageOrders';
import Shop from './pages/Shop'; // Import ShoppingPage component
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import ManageUsers from './pages/ManageUsers';

const App = () => {
  const { isLoggedIn, roles } = useAuth();
  const location = useLocation();
  const isAdmin = roles.includes('Admin');

  return (
    <div>
      <Navbar />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route 
          path="/login" 
          element={isLoggedIn ? <Navigate to={location.state?.from || '/'} replace /> : <Login />} 
        />
        <Route path="/register" element={<Register />} />
        <Route path="/profile" element={isLoggedIn ? <Profile /> : <Navigate to="/login" state={{ from: '/profile' }} />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/payment" element={isLoggedIn ? <PaymentPage /> : <Navigate to="/login" state={{ from: '/payment' }} />} />
        <Route path="/orders" element={isLoggedIn ? <OrdersPage /> : <Navigate to="/login" state={{ from: '/orders' }} />} />
        <Route path="/products" element={isLoggedIn && isAdmin ? <ProductComponent /> : <Navigate to="/products" />} />
        <Route path="/confirm" element={<ConfirmEmail />} />
        <Route path="/confirm-result" element={<ConfirmationResult />} />
        <Route path="/manage-users" element={isLoggedIn && isAdmin ? <ManageUsers /> : <Navigate to="/manage-users" />} />
        <Route path="/manage-orders" element={isLoggedIn && isAdmin ? <ManageOrders /> : <Navigate to="/manage-orders" />} />  
        <Route path="/shop" element={isLoggedIn ? <Shop /> : <Navigate to="/login" state={{ from: '/shop' }} />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
      </Routes>
    </div>
  );
};

export default App;