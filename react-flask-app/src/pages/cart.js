import React, { useEffect, useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import SessionManager from '../components/SessionManager';
import '../css/Cart.css'; // Assuming you have a CSS file for styling

const Cart = () => {
  const { userId, username } = useAuth();
  const [cartItems, setCartItems] = useState([]);
  const [ssid, setSsid] = useState('');

  useEffect(() => {
    const fetchCartItems = async () => {
      try {
        let response;
        if (userId) {
          response = await fetch(`/main/cart?account_id=${userId}`);
        } else {
          response = await fetch(`/main/cart?session_id=${ssid}`);
        }

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Fetched cart items:', data); // Log the fetched data
        setCartItems(data);
      } catch (error) {
        console.error('Error fetching cart items:', error);
      }
    };

    fetchCartItems();
  }, [userId, ssid]);

  const handleRemoveFromCart = async (cartId) => {
    try {
      const response = await fetch(`/main/cart/${cartId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log('Removed from cart:', data);

      // Update the cart items state after deletion
      setCartItems(prevItems => prevItems.filter(item => item.cart_id !== cartId));
    } catch (error) {
      console.error('Error removing from cart:', error);
    }
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
      </main>
      <footer className="cart-page-footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Cart;