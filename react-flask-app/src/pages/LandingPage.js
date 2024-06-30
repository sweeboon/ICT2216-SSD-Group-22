import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import Navbar from './Navbar';
import '../css/LandingPage.css';

const LandingPage = () => {
  const { username, handleLogout } = useAuth();
  const [products, setProducts] = useState([]);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('/main/products'); // Update the API URL if needed
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        const data = await response.json();
        console.log('Fetched products:', data);  // Log the fetched data
        setProducts(data);
      } catch (error) {
        console.error("Error fetching products:", error);
      }
    };

    fetchProducts();
  }, []);

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
          <a href="/shop" className="btn">Shop Now</a>
        </section>
        
        <section>
          <h3>Our Products</h3>
          <div className="product-grid">
            {products.map(product => (
              <div key={product.product_id} className="product-card">
                <img src={product.image_path} alt={product.product_description} className="product-image" />
                <div className="product-info">
                  <p>{product.product_description}</p>
                  <p>${product.product_price}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
      <footer className="landing-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;