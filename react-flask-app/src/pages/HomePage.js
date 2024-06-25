import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Login from './Login';
import Register from './Register';
import LandingPage from './LandingPage';
import AssignRole from './AssignRole';
import '../assets/HomePage.css';

const HomePage = () => {
  const { isLoggedIn, username, handleLogout } = useAuth();

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={isLoggedIn ? <Navigate to="/landing" replace /> : (
            <div className="home">
              <header className="home-header">
                <h1>Welcome to Alcoholic Beverages Store</h1>
                {isLoggedIn ? (
                  <div>
                    <h2>Welcome, {username}!</h2>
                    <button onClick={handleLogout}>Logout</button>
                  </div>
                ) : (
                  <nav>
                    <Link to="/login">Login</Link>
                    <Link to="/register">Register</Link>
                  </nav>
                )}
              </header>
            </div>
          )}
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/assign-role" element={<AssignRole />} />
      </Routes>
    </Router>
  );
};

export default HomePage;
