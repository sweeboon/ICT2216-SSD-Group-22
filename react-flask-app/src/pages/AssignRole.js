import React, { useState, useEffect } from 'react';
import axios from '../components/axiosConfig';
import { useAuth } from '../hooks/useAuth';

const AssignRole = () => {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [error, setError] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const { username } = useAuth();

  useEffect(() => {
    const fetchUsersAndRoles = async () => {
      try {
        const usersResponse = await axios.get('/auth/users');
        const rolesResponse = await axios.get('/auth/roles');
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
      await axios.post('/auth/assign-role', { user_id: selectedUser, role_name: selectedRole });
      setError('');
      // Optionally update users state to reflect the role change immediately
      setUsers(users.map(user => user.user_id === selectedUser ? { ...user, roles: [selectedRole] } : user));
    } catch (error) {
      console.error('Error assigning role:', error);
      setError('Error assigning role');
    }
  };

  return (
    <div>
      <h1>Assign Role to User</h1>
      {error && <p>{error}</p>}
      <div>
        <label>User:</label>
        <select onChange={e => setSelectedUser(e.target.value)} value={selectedUser}>
          <option value="">Select a user</option>
          {users.filter(user => user.email !== username).map(user => (
            <option key={user.user_id} value={user.user_id}>{user.email}</option>
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
