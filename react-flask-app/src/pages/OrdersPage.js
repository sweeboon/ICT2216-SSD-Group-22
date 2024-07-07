import React, { useEffect, useState } from 'react';
import axios from '../components/axiosConfig';
import '../css/Orders.css';

const OrdersPage = () => {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await axios.get('/main/orders');
        setOrders(response.data);
      } catch (error) {
        console.error('Error fetching orders:', error);
      }
    };

    fetchOrders();
  }, []);

  return (
    <div  className="orders-page">
    <main className="orders-container">
      <h2>Your Orders</h2>
      {orders.length > 0 ? (
        <ul>
          {orders.map(order => (
            <li key={order.order_id}>
              <p><strong>Order ID:</strong> {order.order_id}</p>
              <p><strong>Product:</strong> {order.product_description}</p>
              <p><strong>Quantity:</strong> {order.quantity}</p>
              <p><strong>Price:</strong> ${order.order_price.toFixed(2)}</p>
              <p><strong>Status:</strong> {order.order_status}</p>
              <p><strong>Date:</strong> {order.order_date}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p className="no-orders">You have no orders.</p>
      )}
      </main>
                  <footer className="footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default OrdersPage;
