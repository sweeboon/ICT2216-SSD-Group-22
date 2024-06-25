import React, { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import axios from '../components/axiosConfig';
import { useAuth } from '../hooks/useAuth';
import '../assets/Auth.css';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [passwordErrors, setPasswordErrors] = useState([]);
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/auth/register', {
        username,
        email,
        password,
        date_of_birth: dateOfBirth,
        address
      });
      setMessage(response.data.message);
      setError('');
      setPasswordErrors([]);
      navigate('/'); // Redirect to homepage after successful registration
    } catch (error) {
      if (error.response && error.response.data.errors) {
        setPasswordErrors(error.response.data.errors);
      } else {
        setError(error.response.data.message || 'Error occurred during registration');
        setPasswordErrors([]);
      }
      setMessage('');
    }
  };

  if (isLoggedIn) {
    return <Navigate to="/landing" replace />;
  }

  return (
    <div className="auth-container">
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div>
          <label>Email:</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div>
          <label>Date of Birth:</label>
          <input
            type="date"
            value={dateOfBirth}
            onChange={(e) => setDateOfBirth(e.target.value)}
          />
        </div>
        <div>
          <label>Address:</label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
          />
        </div>
        <button type="submit">Register</button>
        {message && <p>{message}</p>}
        {error && <p>{error}</p>}
        {passwordErrors.length > 0 && (
          <ul>
            {passwordErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        )}
      </form>
    </div>
  );
};

export default Register;
