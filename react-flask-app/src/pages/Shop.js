import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import '../css/Shop.css';
import SessionManager from '../components/SessionManager';
import axios from 'axios';

const Shop = () => {
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
    <div className="shop">
      <h1>Product Catalog</h1>
      <div className="product-grid">
        {products.map((product) => (
          <div key={product.product_id} className="product-item">
            <h3>{product.product_description}</h3>
            <p>Price: ${product.product_price}/ bottle</p>
            <img src={product.image_path} alt={product.product_description} 
              style={{ width: '100px', height: '100px' }} />
            <button onClick={() => handleAddToCart(product)} className="cart-btn">Add to Cart</button>
          </div>
        ))}
      </div>
      <button onClick={handleCheckout} className="checkout-btn">
        Go to Cart
      </button>
      <footer className="shop-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
    
  );
};

export default Shop;


