import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useNavigate } from 'react-router-dom';

const PaymentPage = () => {
    const [paymentMethod, setPaymentMethod] = useState('Cash On Delivery');
    const [totalAmount, setTotalAmount] = useState(0);
    const [creditCardNumber, setCreditCardNumber] = useState('');
    const [expiryDate, setExpiryDate] = useState('');
    const [cvv, setCvv] = useState('');
    const [message, setMessage] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        // Fetch the total amount from the backend
        const fetchTotalAmount = async () => {
            try {
                const response = await axios.get('/main/cart/total');
                setTotalAmount(response.data.total_amount);
                setMessage(response.data.message);
                if (response.data.total_amount === 0) {
                    alert(response.data.message);
                    navigate('/shop');  // Redirect to shop page if the cart is empty
                }
            } catch (error) {
                console.error('Error fetching total amount:', error);
                setMessage('Error fetching total amount. Please try again.');
            }
        };

        fetchTotalAmount();
    }, [navigate]);

    const handlePayment = async () => {
        console.log("Credit Card Number:", creditCardNumber);
        console.log("Expiry Date:", expiryDate);
        console.log("CVV:", cvv);

        try {
            const response = await axios.post('/main/payment', {
                payment_method: paymentMethod,
                total_amount: totalAmount,
                credit_card_number: creditCardNumber,
                expiry_date: expiryDate,
                cvv: cvv
            });

            if (response.status === 201) {
                setMessage('Payment successful and order placed!');
                console.log('Payment successful and order placed!');
                navigate('/orders'); // Redirect to orders page after successful payment
            } else {
                setMessage('Failed to process payment.');
                console.log('Failed to process payment.');
            }
        } catch (error) {
            console.error('Payment failed:', error);
            setMessage('Payment failed. Please try again.');
        }
    };

    return (
        <div>
            <h2>Payment Page</h2>
            <p>Total Amount: ${totalAmount}</p>
            <div>
                <label>
                    <input
                        type="radio"
                        value="Cash On Delivery"
                        checked={paymentMethod === 'Cash On Delivery'}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                    Cash On Delivery
                </label>
                <label>
                    <input
                        type="radio"
                        value="Credit Card"
                        checked={paymentMethod === 'Credit Card'}
                        onChange={(e) => setPaymentMethod(e.target.value)}
                    />
                    Credit Card
                </label>
            </div>
            {paymentMethod === 'Credit Card' && (
                <div>
                    <label>
                        Credit Card Number:
                        <input 
                            type="text" 
                            placeholder="1234 5678 9012 3456"
                            value={creditCardNumber}
                            onChange={(e) => setCreditCardNumber(e.target.value)}
                        />
                    </label>
                    <label>
                        Expiry Date:
                        <input 
                            type="text" 
                            placeholder="MM/YY" 
                            value={expiryDate}
                            onChange={(e) => setExpiryDate(e.target.value)}
                        />
                    </label>
                    <label>
                        CVV:
                        <input 
                            type="text" 
                            placeholder="123" 
                            value={cvv}
                            onChange={(e) => setCvv(e.target.value)}
                        />
                    </label>
                </div>
            )}
            <button onClick={handlePayment}>Submit Payment</button>
            {message && <p>{message}</p>}
        </div>
    );
};

export default PaymentPage;
