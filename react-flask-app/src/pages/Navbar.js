import React from 'react';
import { useAuth } from '../hooks/useAuth';
import '../css/Navbar.css';

const Navbar = () => {
  const { username, handleLogout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <a href="/">Over18</a>
      </div>
      <ul className="navbar-links">
        <li><a href="/shop">Shop</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/contact">Contact</a></li>
        <li><button onClick={handleLogout} aria-label="Logout">Logout</button></li>
      </ul>
    </nav>
  );
};

export default Navbar;
