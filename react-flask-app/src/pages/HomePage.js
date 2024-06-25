import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Login from './Login';
import Register from './Register';
import ConfirmEmail from './ConfirmEmail';
import ConfirmationResult from './ConfirmationResult';
import '../assets/HomePage.css';
import LandingPage from './LandingPage';

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
        <Route path="/login" element={isLoggedIn ? <Navigate to="/" replace /> : <Login />} /> {/* If logged in, redirect to Landing Page else show Register */}
        <Route path="/register" element={isLoggedIn ? <Navigate to="/" replace /> : <Register />} /> {/* Show email confirmation components */}
        <Route path="/confirm" element={<ConfirmEmail />} />
        <Route path="/confirmation-result" element={<ConfirmationResult />} />
        <Route path="/landing" element={isLoggedIn ? <LandingPage /> : <Navigate to="/login" replace />} /> {/* Landing Page Route */}
      </Routes>
    </Router>
  );
};

export default HomePage;