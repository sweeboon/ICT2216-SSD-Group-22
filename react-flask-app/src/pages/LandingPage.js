import React from 'react';
import { useAuth } from '../hooks/useAuth';
import Navbar from './NavBar';
import '../css/LandingPage.css';

const LandingPage = () => {
  const { username, handleLogout } = useAuth();

  return (
    <div className="landing-page">
      <Navbar />
      <header className="landing-page-header">
        <h1>Over18</h1>
        <h2>Welcome, {username}!</h2>
      </header>
      <main className="landing-page-content">
        <section>
          <h3>Explore Our Selection of Alcoholic Beverages</h3>
          <p>Discover a wide range of beers, wines, and spirits from around the world.</p>
          <a href="/shop" className="btn">
            Shop Now
          </a>
        </section>
      </main>
      <footer className="landing-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
