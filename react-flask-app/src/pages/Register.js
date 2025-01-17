import React, { useState } from 'react';
import '../css/Auth.css';
import axios from '../components/axiosConfig';
import validator from 'validator';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [address, setAddress] = useState('');
  const [error, setError] = useState('');
  const [registered, setRegistered] = useState(false);

  const validatePassword = (password) => {
    const minLength = 12;
    const hasNumber = /\d/;
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/;
    const hasAlphabet = /[a-zA-Z]/;

    if (password.length < minLength) {
      return 'Password must be at least 8 characters long.';
    }
    if (!hasNumber.test(password)) {
      return 'Password must contain at least one number.';
    }
    if (!hasSpecialChar.test(password)) {
      return 'Password must contain at least one special character.';
    }
    if (!hasAlphabet.test(password)) {
      return 'Password must contain at least one alphabet.';
    }
    return null;
  };


  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password || !username || !dateOfBirth || !address) {
      setError('All fields are required.');
      return;
    }

    if (!validator.isEmail(email)) {
      setError('Invalid email format.');
      return;
    }

    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }

    try {
      const sanitizedEmail = validator.normalizeEmail(email);
      const sanitizedUsername = validator.escape(username);
      const sanitizedAddress = validator.escape(address);
      const sanitizedDateOfBirth = validator.escape(dateOfBirth); // Sanitize date_of_birth

      const response = await axios.post('/auth/register', {
        email: sanitizedEmail,
        password,
        username: sanitizedUsername,
        date_of_birth: sanitizedDateOfBirth,
        address: sanitizedAddress,
      });

      console.log('Registration response:', response.data);
      setRegistered(true);
    } catch (error) {
      console.error('Registration failed:', error);
      setError('Registration failed. Please try again.');
    }
  };

  if (registered) {
    return <div className="content"><h2
    style={{
      color: '#333',
      fontSize: '24px',
      textAlign: 'center',
      backgroundColor: 'rgba(255, 255, 255, 0.8)',
      padding: '20px',
      boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)'
    }}
  >Registration Successful!</h2>
          <footer className="footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer></div>;
  }

  return (
    <div className="register">
      <div className="content">
        <div className="auth-container">
          <h2>Register</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Username:</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Email:</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Password:</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Date of Birth:</label>
              <input
                type="date"
                value={dateOfBirth}
                onChange={(e) => setDateOfBirth(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Address:</label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                required
              />
            </div>
            <button type="submit">Register</button>
            {error && <p className="error">{error}</p>}
          </form>
        </div>
      </div>
      <footer className="footer">
        <p>&copy; 2024 Over18. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default Register;
