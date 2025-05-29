import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import useAuthStore from '../store/authStore';

const PrivateRoute = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  // Check token and user presence as well, not just isAuthenticated flag initially
  // because initialize() might set isAuthenticated based on token presence alone.
  // A more robust check might involve verifying token validity or user object completeness.
  const token = useAuthStore((state) => state.token);
  const user = useAuthStore((state) => state.user);

  if (!isAuthenticated || !token) {
    // Redirect them to the /login page, but save the current location they were
    // trying to go to when they were redirected. This allows us to send them
    // along to that page after they login, which is a nicer user experience
    // than dropping them off on the home page.
    return <Navigate to="/login" replace />;
  }
  
  // If user object is null/empty but token exists, you might want to trigger
  // a fetch for user details or show a loading state before rendering Outlet.
  // For now, we assume if token exists, it's okay.

  return <Outlet />;
};

export default PrivateRoute;
