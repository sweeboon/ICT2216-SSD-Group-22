import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from '../components/axiosConfig';
import SessionManager from '../components/SessionManager';

const Cart = () => {
  const { isLoggedIn, username } = useAuth();
  const [cartItems, setCartItems] = useState([]);
  const [ssid, setSsid] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const session_id = location.state?.session_id || ssid;

  useEffect(() => {
    const fetchCartItems = async () => {
      try {
        let response;
        const token = localStorage.getItem('session_token');
        if (isLoggedIn) {
          if (session_id) {
            await axios.post('/main/cart/transfer', { session_id }, {
              headers: { Authorization: `Bearer ${token}` }
            });
          }
          response = await axios.get('/main/cart', {
            headers: { Authorization: `Bearer ${token}` }
          });
        } else {
          response = await axios.get(`/main/cart?session_id=${session_id}`);
        }
        setCartItems(response.data);
      } catch (error) {
        console.error('Error fetching cart items:', error);
      }
    };

    fetchCartItems();
  }, [session_id, isLoggedIn]);

  const handleRemoveFromCart = async (cartId) => {
    try {
      await axios.delete(`/main/cart/${cartId}`);
      setCartItems((prevItems) => prevItems.filter((item) => item.cart_id !== cartId));
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  };

  const handleCheckout = async () => {
    if (!isLoggedIn) {
      navigate('/login', { state: { from: '/cart', session_id } });
      return;
    }
    navigate('/payment');
  };

  return (
    <div className="cart-page">
      <SessionManager setSsid={setSsid} />
      <header className="cart-page-header">
        <h1>Over18 Cart</h1>
        <h2>Welcome, {username ? username : 'Guest'}!</h2>
      </header>
      <main className="cart-page-content">
        <section>
          <h3>Your Cart</h3>
          {cartItems.length > 0 ? (
            <div className="cart-grid">
              {cartItems.map((item) => (
                <div key={item.cart_id} className="cart-card">
                  <img src={item.image_path} alt={item.product_description} className="cart-image" />
                  <div className="cart-info">
                    <p>{item.product_description}</p>
                    <p>${item.cart_item_price.toFixed(2)}</p>
                    <button onClick={() => handleRemoveFromCart(item.cart_id)} className="btn">
                      Remove from Cart
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p>Your cart is currently empty.</p>
          )}
        </section>
        <button onClick={handleCheckout} className="btn">
          Checkout
        </button>
      </main>
      <footer className="cart-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Cart;
