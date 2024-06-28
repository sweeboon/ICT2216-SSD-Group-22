import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import Login from './Login';
import Register from './Register';
import LandingPage from './LandingPage';
import AssignRole from './AssignRole';
import ConfirmEmail from './ConfirmEmail';
import ConfirmationResult from './ConfirmationResult';
import Profile from './Profile';
import '../assets/HomePage.css';
import Navbar from './NavBar';

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
                <Navbar />
                <h1>Over18</h1>
                <h2>Login/ Register now to start purchasing alcoholic beverages</h2>
              </header>
              <main className='home-content'>
              <Link to="/login" className="btn">
            Login
          </Link>
          <span className="button-spacing"></span>
          <Link to="/register" className="btn">
            Register
          </Link>
              </main>
              <footer className="landing-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
            </div>
          )}
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/landing" element={<LandingPage />} />
        <Route path="/assign-role" element={<AssignRole />} />
        <Route path="/confirm" element={<ConfirmEmail />} />
        <Route path="/confirmation-result" element={<ConfirmationResult />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </Router>
  );
};

export default HomePage;
