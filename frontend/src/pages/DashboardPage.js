import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import baseService from '../services/baseService';
import useAuthStore from '../store/authStore';
import useAppStore from '../store/appStore'; // Import the new app store

const DashboardPage = () => {
  const [bases, setBases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const user = useAuthStore((state) => state.user);
  const navigate = useNavigate();
  const setCurrentBaseId = useAppStore((state) => state.setCurrentBaseId);

  useEffect(() => {
    const fetchUserBases = async () => {
      try {
        setLoading(true);
        setError('');
        const userBases = await baseService.getBases();
        setBases(userBases);
      } catch (err) {
        setError(typeof err === 'string' ? err : (err.detail || err.message || 'Failed to fetch bases.'));
      } finally {
        setLoading(false);
      }
    };

    fetchUserBases();
  }, []);

  const handleBaseClick = (baseId) => {
    // setCurrentBaseId will also trigger fetching tables for this base
    // No need to call it here, store action handles it.
    // setCurrentBaseId(baseId);
    navigate(`/bases/${baseId}`);
  };

  if (loading) {
    return <div style={{ padding: '2rem', className: 'container' }}>Loading dashboard...</div>;
  }

  if (error) {
    return <div style={{ padding: '2rem', color: 'red', className: 'container' }}>Error: {error}</div>;
  }

  return (
    <div style={{ padding: '2rem' }} className="container">
      <h2>Dashboard</h2>
      <p>Welcome, {user?.email || 'User'}!</p>
      <h3>Your Bases:</h3>
      {bases.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {bases.map((base) => (
            <li
              key={base.id}
              onClick={() => handleBaseClick(base.id)}
              style={{
                padding: '10px',
                border: '1px solid #ddd',
                marginBottom: '5px',
                cursor: 'pointer',
                borderRadius: '4px',
                backgroundColor: '#f9f9f9'
              }}
              onMouseEnter={e => e.currentTarget.style.backgroundColor = '#eef'}
              onMouseLeave={e => e.currentTarget.style.backgroundColor = '#f9f9f9'}
            >
              {base.name}
            </li>
          ))}
        </ul>
      ) : (
        <p>You don't have any bases yet.</p>
      )}
      {/* Add functionality to create new bases later if needed on this page */}
    </div>
  );
};

export default DashboardPage;
