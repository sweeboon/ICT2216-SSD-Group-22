import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useAuth } from '../hooks/useAuth';

const Profile = () => {
  const { isLoggedIn, username } = useAuth();
  const [profile, setProfile] = useState({
    name: '',
    address: '',
    date_of_birth: '',
    email: '',
    original_email: ''
  });
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [otpRequired, setOtpRequired] = useState(false);
  const [changeType, setChangeType] = useState('');
  const [otpVerified, setOtpVerified] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get('/profile');
        setProfile({ ...response.data, original_email: response.data.email });
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

  const handlePasswordChange = (e) => {
    setNewPassword(e.target.value);
  };

  const handleConfirmPasswordChange = (e) => {
    setConfirmPassword(e.target.value);
  };

  const requestOtp = async (changeType, newEmail = null) => {
    try {
      const response = await axios.post('/profile/request-otp', { change_type: changeType, new_email: newEmail });
      alert(response.data.message);
      setOtpRequired(true);
      setChangeType(changeType);
    } catch (error) {
      console.error('Error requesting OTP:', error);
      setError('Failed to request OTP');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form submission
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (profile.email !== profile.original_email) {
      requestOtp('email', profile.email);
    } else if (newPassword !== '') {
      requestOtp('password');
    } else {
      updateProfile();
    }
  };

  const updateProfile = async () => {
    try {
      const data = { ...profile };
      delete data.original_email; // Remove original_email from the payload

      if (profile.email === profile.original_email) {
        delete data.email; // Remove email if it hasn't changed
      }

      if (otpVerified && changeType === 'password') {
        data.password = newPassword;
        data.confirm_password = confirmPassword;
      }

      const response = await axios.put('/profile', data);
      alert(response.data.message);
      setOtpVerified(false);
    } catch (error) {
      console.error('Error updating profile:', error);
      setError('Failed to update profile');
    }
  };

  const handleVerifyOtp = async () => {
    try {
      const response = await axios.post('/profile/verify-otp', { otp, change_type: changeType, new_password: newPassword, confirm_password: confirmPassword });
      alert(response.data.message);
      setOtp('');
      setOtpRequired(false);
      setOtpVerified(true);
      if (changeType === 'email' || changeType === 'password') {
        updateProfile();
      }
    } catch (error) {
      console.error('Error verifying OTP:', error);
      setError('Failed to verify OTP');
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
        <div>
          <label>New Password:</label>
          <input
            type="password"
            name="newPassword"
            value={newPassword}
            onChange={handlePasswordChange}
          />
        </div>
        <div>
          <label>Confirm New Password:</label>
          <input
            type="password"
            name="confirmPassword"
            value={confirmPassword}
            onChange={handleConfirmPasswordChange}
          />
        </div>
        <button type="submit">Update Profile</button>
        {otpRequired && (
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
        {error && <p>{error}</p>}
      </form>
    </div>
  );
};

export default Profile;
