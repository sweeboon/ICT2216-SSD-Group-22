import React from 'react';
import { useAuth } from '../hooks/useAuth';

const LandingPage = () => {
  const { username, handleLogout } = useAuth();

  return (
    <div className="landing-page">
      <header className="landing-page-header">
        <h1>Welcome to the Online Beer Store</h1>
        <h2>Welcome, {username}!</h2>
        <button onClick={handleLogout}>Logout</button>
      </header>
    </div>
  );
};

export default LandingPage;