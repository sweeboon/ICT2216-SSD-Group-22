import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import '../css/Navbar.css';

const Navbar = () => {
  const { isLoggedIn, roles, handleLogout } = useAuth();
  const isAdmin = roles.includes('Admin');

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <a href="/">Over18</a>
      </div>
      <ul className="navbar-links">
        <li><Link to="/shop">Shop</Link></li>
        {isLoggedIn && <li><Link to="/cart">Cart</Link></li>}
        {isLoggedIn && <li><Link to="/orders">Orders</Link></li>}
        {isLoggedIn && <li><Link to="/profile">Profile</Link></li>}
        {isAdmin && <li><Link to="/manage-users">Manage Users</Link></li>}
        {isAdmin && <li><Link to="/manage-orders">Manage Orders</Link></li>}
        {isAdmin && <li><Link to="/products">Manage Products</Link></li>}
        {!isLoggedIn && <li><Link to="/login">Login</Link></li>}
        {!isLoggedIn && <li><Link to="/register">Register</Link></li>}
        {isLoggedIn && (
          <li><button onClick={handleLogout} aria-label="Logout">Logout</button></li>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
