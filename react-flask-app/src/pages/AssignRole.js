import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useAuth } from '../hooks/useAuth';

const AssignRole = () => {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const { username } = useAuth();

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

  const handleAssignRole = async () => {
    try {
      await axios.post('/admin/assign-role', { account_id: selectedUser, role_name: selectedRole });
      setError('');
      setSuccess(`Role ${selectedRole} assigned to user successfully`);
      setUsers(users.map(user => user.account_id === selectedUser ? { ...user, roles: [selectedRole] } : user));
    } catch (error) {
      console.error('Error assigning role:', error);
      setError('Error assigning role');
      setSuccess('');
    }
  };

  const handleUserChange = async (e) => {
    const userId = e.target.value;
    setSelectedUser(userId);
    setSelectedRole('');
    setSuccess('');

    const selectedUser = users.find(user => user.account_id === userId);
    if (selectedUser && selectedUser.roles.length > 0) {
      setSelectedRole(selectedUser.roles[0]);
    }
  };

  return (
    <div>
      <h1>Assign Role to User</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {success && <p style={{ color: 'green' }}>{success}</p>}
      <div>
        <label>User:</label>
        <select onChange={handleUserChange} value={selectedUser}>
          <option value="">Select a user</option>
          {users.filter(user => user.email !== username).map(user => (
            <option key={user.account_id} value={user.account_id}>{user.email}</option>
          ))}
        </select>
      </div>
      <div>
        <label>Role:</label>
        <select onChange={e => setSelectedRole(e.target.value)} value={selectedRole}>
          <option value="">Select a role</option>
          {roles.map(role => (
            <option key={role.id} value={role.name}>{role.name}</option>
          ))}
        </select>
      </div>
      <button onClick={handleAssignRole}>Assign Role</button>
    </div>
  );
};

export default AssignRole;
