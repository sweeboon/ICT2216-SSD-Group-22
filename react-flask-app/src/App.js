import React from 'react';
import { Route, Routes, Navigate, useLocation } from 'react-router-dom';
import HomePage from './pages/HomePage';
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
import AssignRole from './pages/AssignRole';  // Import AssignRole component
import { useAuth } from './hooks/useAuth';
import Navbar from './pages/Navbar';
import ManageOrders from './pages/ManageOrders';

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
        <Route path="/assign-role" element={isLoggedIn && isAdmin ? <AssignRole /> : <Navigate to="/assign-role" />} />  
        <Route path="/manage-orders" element={isLoggedIn && isAdmin ? <ManageOrders /> : <Navigate to="/manage-orders" />} />  
      </Routes>
    </div>
  );
};

export default App;
