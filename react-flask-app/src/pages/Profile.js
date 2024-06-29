import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useAuth } from '../hooks/useAuth';

const Profile = () => {
  const { isLoggedIn, username } = useAuth();
  const [profile, setProfile] = useState({
    name: '',
    address: '',
    date_of_birth: '',
    email: ''
  });
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [otpRequested, setOtpRequested] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get('/profile');
        setProfile(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
      }
    };

    fetchProfile();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleRequestOtp = async () => {
    try {
      const response = await axios.post('/auth/request-email-change', { email: profile.email });
      setOtpRequested(true);
      alert(response.data.message);
    } catch (error) {
      console.error('Error requesting OTP:', error);
      setError('Failed to request OTP');
    }
  };

  const handleVerifyOtp = async () => {
    try {
      const response = await axios.post('/profile/change-email', { otp });
      alert(response.data.message);
      setOtp('');
      setOtpRequested(false);
    } catch (error) {
      console.error('Error verifying OTP:', error);
      setError('Failed to verify OTP');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.log('Updating profile with data:', profile);
      const response = await axios.put('/profile', profile);
      alert(response.data.message);
    } catch (error) {
      console.error('Error updating profile:', error);
      setError('Failed to update profile');
    }
  };

  return (
    <div className="profile-container">
      <h2>Profile</h2>
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
          <label>Date of Birth:</label>
          <input
            type="date"
            name="date_of_birth"
            value={profile.date_of_birth}
            onChange={handleChange}
          />
        </div>
        <div>
          <label>Email:</label>
          <input
            type="email"
            name="email"
            value={profile.email}
            onChange={handleChange}
          />
        </div>
        <button type="button" onClick={handleRequestOtp}>Request OTP for Email Change</button>
        {otpRequested && (
          <div>
            <label>Enter OTP:</label>
            <input
              type="text"
              name="otp"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
            />
            <button type="button" onClick={handleVerifyOtp}>Verify OTP</button>
          </div>
        )}
        <button type="submit">Update Profile</button>
        {error && <p>{error}</p>}
      </form>
    </div>
  );
};

export default Profile;
