import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import '../assets/HomePage.css';
import Login from './Login';
import Register from './Register';

function Home() {
  const [products, setProducts] = useState([]);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await axios.get('/auth/protected');
        setUsername(response.data.logged_in_as);
      } catch (error) {
        console.log('No active session');
      }
    };

    checkSession();

    setProducts([
      { id: 1, name: 'Whiskey', price: '$50', image: 'whiskey.jpg' },
      { id: 2, name: 'Wine', price: '$20', image: 'wine.jpg' },
      { id: 3, name: 'Beer', price: '$10', image: 'beer.jpg' },
    ]);
  }, []);

  const handleLogout = async () => {
    await axios.post('/auth/logout');
    setUsername('');
  };

  return (
    <div className="home">
      <header className="home-header">
        <h1>Welcome to Alcoholic Beverages Store</h1>
        {username ? (
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
      <main>
        <div className="products-grid">
          {products.map(product => (
            <div key={product.id} className="product-card">
              <img src={product.image} alt={product.name} className="product-image" />
              <h2>{product.name}</h2>
              <p>{product.price}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

function HomePage() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </Router>
  );
}

export default HomePage;
