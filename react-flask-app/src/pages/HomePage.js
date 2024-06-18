import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link, Navigate} from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useProducts } from '../hooks/useProducts';
import Login from './Login';
import Register from './Register';
import ProtectedRoute from '../components/ProtectedRoute';
import '../assets/HomePage.css';

const HomePage = () => {
  const { isLoggedIn, username, handleLogout } = useAuth();
  const products = useProducts();

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
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
                <main>
                  <div className="products-grid">
                    {products.map((product) => (
                      <div key={product.id} className="product-card">
                        <img src={product.image} alt={product.name} className="product-image" />
                        <h2>{product.name}</h2>
                        <p>{product.price}</p>
                      </div>
                    ))}
                  </div>
                </main>
              </div>
          }
        />
        <Route path="/login" element={isLoggedIn ? <Navigate to="/" replace /> : <Login />} />
        <Route path="/register" element={isLoggedIn ? <Navigate to="/" replace /> : <Register />} />
      </Routes>
    </Router>
  );
};

export default HomePage;
