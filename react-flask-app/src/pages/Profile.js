import React, { useEffect, useState } from 'react';
import axios from '../components/axiosConfig';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Profile = () => {
  const [profile, setProfile] = useState({ name: '', address: '', date_of_birth: '' });
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get('/profile');
        setProfile(response.data);
      } catch (error) {
        setError('Failed to fetch profile');
      }
    };

    if (isLoggedIn) {
      fetchProfile();
    } else {
      navigate('/login');
    }
  }, [isLoggedIn, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile(prevState => ({ ...prevState, [name]: value }));
  };

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put('/profile/profile', {
        ...profile,
        password: password ? password : undefined
      });
      setMessage(response.data.message);
      setError('');
      setPassword('');
    } catch (error) {
      setError(error.response.data.error || 'Failed to update profile');
      setMessage('');
    }
  };

  return (
    <div className="profile-container">
      <h2>Profile</h2>
      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Name:</label>
          <input
            type="text"
            name="name"
            value={profile.name}
            onChange={handleChange}
          />
        </div>
        <div>
          <label>Address:</label>
          <input
            type="text"
            name="address"
            value={profile.address}
            onChange={handleChange}
          />
        </div>
        <div>
          <label>New Password:</label>
          <input
            type="password"
            name="password"
            value={password}
            onChange={handlePasswordChange}
          />
        </div>
        <button type="submit">Update Profile</button>
      </form>
    </div>
  );
};

export default Profile;
