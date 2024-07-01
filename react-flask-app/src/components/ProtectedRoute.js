import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const ProtectedRoute = ({ element, roles = [] }) => {
  const { isLoggedIn, roles: userRoles } = useAuth();

  if (!isLoggedIn) {
    return <Navigate to="/login" />;
  }

  if (roles.length > 0 && !roles.some(role => userRoles.includes(role))) {
    return <Navigate to="/" />;
  }

  return element;
};

export default ProtectedRoute;
