import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import Navbar from './Navbar';
import '../css/LandingPage.css';
import SessionManager from '../components/SessionManager';

const LandingPage = () => {
  const { userId, username } = useAuth(); // Assuming useAuth returns userId as well
  const [products, setProducts] = useState([]);
  const [ssid, setSsid] = useState('');

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('/main/products');
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const data = await response.json();
        setProducts(data);
      } catch (error) {
        console.error("Error fetching products:", error);
      }
    };

    fetchProducts();
  }, []);

  const handleAddToCart = async (product) => {
    const cartAccountId = userId ? userId : ssid;
    const cartSessionId = userId ? null : ssid;
    
    const cartItem = {
      product_id: product.product_id,
      account_id: userId ? userId : null,
      session_id: !userId ? ssid : null,
      quantity: 1,
      cart_item_price: product.product_price, // Assuming price is per item
    };

    try {
      const response = await fetch('/main/cart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(cartItem),
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      console.log('Added to cart:', data);
    } catch (error) {
      console.error("Error adding to cart:", error);
    }
  };

  return (
    <div className="landing-page">
      <Navbar />
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
      </main>
      <footer className="landing-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default LandingPage;