import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from '../components/axiosConfig';
import '../css/Cart.css';

const Cart = () => {
  const { isLoggedIn, username } = useAuth();
  const [cartItems, setCartItems] = useState([]);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCartItems = async () => {
      try {
        if (isLoggedIn) {
          const response = await axios.get('/main/cart');
          setCartItems(response.data);
        } else {
          console.log('User is not logged in, cannot fetch cart items.');
        }
      } catch (error) {
        console.error('Error fetching cart items:', error);
      }
    };

    fetchCartItems();
  }, [isLoggedIn]);

  const handleRemoveFromCart = async (cartId) => {
    try {
      await axios.delete(`/main/cart/${cartId}`);
      setCartItems((prevItems) => prevItems.filter((item) => item.cart_id !== cartId));
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
  };
  

  const handleCheckout = () => {
    if (!isLoggedIn) {
      navigate('/login');
    } else {
      navigate('/payment');
    }
  };
  
  return (
    <div className="cart-page">
      <main className="cart-page-content">
        <section>
          <h3>Your Cart</h3>
          {cartItems.length > 0 ? (
            <div className="cart-items">
              {cartItems.map((item) => (
                <div key={item.cart_id} className="cart-item">
                  <img src={item.image_path} alt={item.product_description} className="cart-image" />
                  <div className="cart-info">
                    <h2>{item.product_description}</h2>
                    <p>Quantity: {item.quantity}</p>
                    <p>Total: ${item.cart_item_price.toFixed(2)}</p>
                    <button onClick={() => handleRemoveFromCart(item.cart_id)} className="btn remove-btn">
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
        {cartItems.length > 0 && (
          <button onClick={handleCheckout} className="btn checkout-btn">
            Checkout
          </button>
        )}
      </main>
      <footer className="cart-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Cart;