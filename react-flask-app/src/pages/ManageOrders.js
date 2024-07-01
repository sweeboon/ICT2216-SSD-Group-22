import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useAuth } from '../hooks/useAuth';

const ManageOrders = () => {
  const [orders, setOrders] = useState([]);
  const [error, setError] = useState('');
  const { username, roles } = useAuth();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await axios.get('/admin/orders');
        setOrders(response.data);
      } catch (error) {
        console.error('Error fetching orders:', error);
        setError('Error fetching orders');
      }
    };

    fetchOrders();
  }, []);

  const handleStatusChange = async (orderId, newStatus) => {
    try {
      await axios.put(`/admin/orders/${orderId}/status`, { status: newStatus });
      setOrders(orders.map(order => 
        order.order_id === orderId ? { ...order, order_status: newStatus } : order
      ));
    } catch (error) {
      console.error('Error updating order status:', error);
      setError('Error updating order status');
    }
  };

  if (!roles.includes('Admin') && !roles.includes('SuperAdmin')) {
    return <p>You do not have permission to view this page.</p>;
  }

  return (
    <div>
      <h1>Manage Orders</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Order ID</th>
            <th>User Email</th>
            <th>Product ID</th>
            <th>Status</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Payment Method</th>
            <th>Total Amount</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {orders.map(order => (
            <tr key={order.order_id}>
              <td>{order.order_id}</td>
              <td>{order.account_email}</td>
              <td>{order.product_id}</td>
              <td>{order.order_status}</td>
              <td>{order.order_price}</td>
              <td>{order.quantity}</td>
              <td>{order.payment_method}</td>
              <td>{order.total_amount}</td>
              <td>
                {order.order_status === 'Pending' ? (
                  <button onClick={() => handleStatusChange(order.order_id, 'Completed')}>
                    Mark as Completed
                  </button>
                ) : (
                  <span>Completed</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ManageOrders;
