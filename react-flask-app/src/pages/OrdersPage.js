import React, { useEffect, useState } from 'react';
import axios from '../components/axiosConfig';

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
    <div>
      <h2>Your Orders</h2>
      {orders.length > 0 ? (
        <ul>
          {orders.map(order => (
            <li key={order.order_id}>
              <p>Order ID: {order.order_id}</p>
              <p>Product: {order.product_description}</p>
              <p>Quantity: {order.quantity}</p>
              <p>Price: ${order.order_price.toFixed(2)}</p>
              <p>Status: {order.order_status}</p>
              <p>Date: {order.order_date}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>You have no orders.</p>
      )}
    </div>
  );
};

export default OrdersPage;
