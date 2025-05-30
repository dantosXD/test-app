import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import useAppStore from '../store/appStore'; // Import appStore
import authService from '../services/authService';

const Navbar = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const clearAppStoreData = useAppStore((state) => state.clearCurrentBaseAndTable); // Get action

  const handleLogout = () => {
    authService.logout(); // Clears auth store
    clearAppStoreData(); // Clears app specific data
    navigate('/login');
  };

  return (
    <nav style={{ padding: '1rem', background: '#eee', display: 'flex', justifyContent: 'space-between' }}>
      <div>
        <Link to={isAuthenticated ? "/" : "/login"} style={{ marginRight: '1rem', textDecoration: 'none', color: 'blue' }}>
          Airtable Clone
        </Link>
      </div>
      <div>
        {isAuthenticated ? (
          <>
            <span style={{ marginRight: '1rem' }}>Welcome, {user?.email || 'User'}!</span>
            <Link to="/" style={{ marginRight: '1rem', textDecoration: 'none', color: 'blue' }}>Dashboard</Link>
            <button onClick={handleLogout} style={{ background: 'transparent', border: '1px solid blue', color: 'blue', cursor: 'pointer' }}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ marginRight: '1rem', textDecoration: 'none', color: 'blue' }}>Login</Link>
            <Link to="/register" style={{ textDecoration: 'none', color: 'blue' }}>Register</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
