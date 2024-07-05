import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import '../css/LandingPage.css';
import SessionManager from '../components/SessionManager';
import axios from 'axios';

const LandingPage = () => {
  const { isLoggedIn, username } = useAuth();
  const [products, setProducts] = useState([]);
  const [ssid, setSsid] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await axios.get('/main/products');
        setProducts(response.data);
      } catch (error) {
        console.error('Error fetching products:', error);
      }
    };

    fetchProducts();
  }, []);

  const handleAddToCart = async (product) => {
    const cartItem = {
      product_id: product.product_id,
      account_id: null,
      session_id: ssid,
      quantity: 1,
      cart_item_price: product.product_price,
    };

    try {
      await axios.post('/main/cart', cartItem);
      console.log('Added to cart');
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  const handleCheckout = () => {
    navigate('/cart', { state: { session_id: ssid } });
  };

  return (
    <div className="landing-page">
      <SessionManager setSsid={setSsid} />
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
                  <button onClick={() => handleAddToCart(product)} className="btn">Add to Cart</button>
                </div>
              </div>
            ))}
          </div>
        </section>
        <button onClick={handleCheckout} className="btn">
          Go to Cart
        </button>
      </main>
      <footer className="landing-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
