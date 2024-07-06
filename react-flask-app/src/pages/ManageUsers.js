import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useAuth } from '../hooks/useAuth';

const ManageUsers = () => {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    name: '',
    address: '',
    password: '',
    role: ''
  });
  const { username, roles: userRoles } = useAuth();

  useEffect(() => {
    const fetchUsersAndRoles = async () => {
      try {
        const usersResponse = await axios.get('/admin/users');
        const rolesResponse = await axios.get('/admin/roles');
        setUsers(usersResponse.data);
        setRoles(rolesResponse.data);
      } catch (error) {
        console.error('Error fetching users and roles:', error);
        setError('Error fetching users and roles');
      }
    };

    fetchUsersAndRoles();
  }, []);

  const handleUserSelect = (e) => {
    const userId = e.target.value;
    const user = users.find(user => user.account_id == userId);
    
    if (user) {
      setSelectedUser(user);
      setFormData({
        email: user.email,
        name: user.name,
        address: user.address,
        password: '',
        role: user.roles[0] || ''
      });
      setSuccess('');
    } else {
      setSelectedUser(null);
      setFormData({
        email: '',
        name: '',
        address: '',
        password: '',
        role: ''
      });
      setError('User not found');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleRoleChange = async () => {
    try {
      await axios.post('/admin/assign-role', { account_id: selectedUser.account_id, role_name: formData.role });
      setSuccess(`Role ${formData.role} assigned to user successfully`);
      setUsers(users.map(user => user.account_id === selectedUser.account_id ? { ...user, roles: [formData.role] } : user));
    } catch (error) {
      console.error('Error assigning role:', error);
      setError('Error assigning role');
      setSuccess('');
    }
  };

  const handleUserUpdate = async () => {
    try {
      await axios.put(`/admin/users/${selectedUser.account_id}`, {
        email: formData.email,
        name: formData.name,
        address: formData.address,
        password: formData.password
      });
      setSuccess('User updated successfully');
      setUsers(users.map(user => user.account_id === selectedUser.account_id ? { ...user, ...formData, roles: [formData.role] } : user));
    } catch (error) {
      console.error('Error updating user:', error);
      setError('Error updating user');
      setSuccess('');
    }
  };

  const handleUserDelete = async () => {
    try {
      await axios.delete(`/admin/users/${selectedUser.account_id}`);
      setSuccess('User deleted successfully');
      setUsers(users.filter(user => user.account_id !== selectedUser.account_id));
      setSelectedUser(null);
      setFormData({ email: '', name: '', address: '', password: '', role: '' });
    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Error deleting user');
      setSuccess('');
    }
  };

  return (
    <div>
      <h1>Manage Users</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}
      <div>
        <label>User:</label>
        <select onChange={handleUserSelect} value={selectedUser ? selectedUser.account_id : ''}>
          <option value="">Select a user</option>
          {users.filter(user => !user.roles.includes('Admin')).map(user => (
            <option key={user.account_id} value={user.account_id}>{user.email}</option>
          ))}
        </select>
      </div>
      {selectedUser && (
        <div>
          <div>
            <label>Email:</label>
            <input type="email" name="email" value={formData.email} onChange={handleInputChange} disabled={selectedUser.roles.includes('Admin')} />
          </div>
          <div>
            <label>Name:</label>
            <input type="text" name="name" value={formData.name} onChange={handleInputChange} disabled={selectedUser.roles.includes('Admin')} />
          </div>
          <div>
            <label>Address:</label>
            <input type="text" name="address" value={formData.address} onChange={handleInputChange} disabled={selectedUser.roles.includes('Admin')} />
          </div>
          <div>
            <label>Password:</label>
            <input type="password" name="password" value={formData.password} onChange={handleInputChange} disabled={selectedUser.roles.includes('Admin')} />
          </div>
          <div>
            <label>Role:</label>
            <select name="role" value={formData.role} onChange={handleInputChange} disabled={selectedUser.roles.includes('Admin')}>
              <option value="">Select a role</option>
              {roles.map(role => (
                <option key={role.id} value={role.name}>{role.name}</option>
              ))}
            </select>
          </div>
          <button onClick={handleRoleChange} disabled={selectedUser.roles.includes('Admin')}>Assign Role</button>
          <button onClick={handleUserUpdate} disabled={selectedUser.roles.includes('Admin')}>Update User</button>
          <button onClick={handleUserDelete} disabled={selectedUser.roles.includes('Admin')}>Delete User</button>
        </div>
      )}
    </div>
  );
};

export default ManageUsers;
