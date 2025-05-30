import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import useAppStore from '../store/appStore';
import useAuthStore from '../store/authStore'; // For user info, if needed for context

const BaseDetailPage = () => {
  const { baseId } = useParams();
  const navigate = useNavigate();

  const {
    currentBaseId,
    tables,
    isLoadingTables,
    errorTables,
    setCurrentBaseId,
    addTable,
    // setCurrentTableId // Not used directly here, but in table click
  } = useAppStore();

  const base = useAppStore(state => state.tables.length > 0 && state.currentBaseId === parseInt(baseId) ?
    { id: state.currentBaseId, name: "Base " + state.currentBaseId } : null // Placeholder for base name
  );
  // Ideally, fetch base details (name) separately or pass from dashboard. For now, use ID.
  // Or find it from a list of bases if that's stored globally.
  // For this example, we'll just display "Base [ID]" or try to find it if bases were stored from dashboard.

  const [newTableName, setNewTableName] = useState('');

  useEffect(() => {
    const numBaseId = parseInt(baseId);
    if (isNaN(numBaseId)) {
        navigate('/dashboard'); // Or a 404 page
        return;
    }
    // Set current base ID in store if not set or different. This also fetches tables.
    if (currentBaseId !== numBaseId) {
        setCurrentBaseId(numBaseId);
    }
  }, [baseId, currentBaseId, setCurrentBaseId, navigate]);

  const handleCreateTable = async (e) => {
    e.preventDefault();
    if (!newTableName.trim()) return;
    await addTable(parseInt(baseId), newTableName);
    setNewTableName('');
  };

  const handleTableClick = (tableId) => {
    // setCurrentTableId(tableId); // This will be called by store when navigating
    navigate(`/tables/${tableId}`);
  };

  // Find the actual base name if possible (e.g., from a list of all bases if fetched in dashboard)
  // This example assumes base name is not critical or would be fetched separately.
  // We can use a placeholder name for now.
  const currentBaseName = `Base ${baseId}`; // Placeholder

  if (isLoadingTables && tables.length === 0) { // Show loading only if tables are truly empty
    return <div className="container">Loading tables for {currentBaseName}...</div>;
  }

  if (errorTables) {
    return <div className="container" style={{ color: 'red' }}>Error loading tables: {errorTables}</div>;
  }

  return (
    <div className="container" style={{ padding: '2rem' }}>
      <h2>{currentBaseName}</h2>
      <h3 style={{marginTop: '2rem'}}>Tables:</h3>
      {tables.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {tables.map((table) => (
            <li
              key={table.id}
              onClick={() => handleTableClick(table.id)}
              style={{
                padding: '10px', border: '1px solid #ddd', marginBottom: '5px', cursor: 'pointer',
                borderRadius: '4px', backgroundColor: '#f9f9f9'
              }}
              onMouseEnter={e => e.currentTarget.style.backgroundColor = '#eef'}
              onMouseLeave={e => e.currentTarget.style.backgroundColor = '#f9f9f9'}
            >
              {table.name} (ID: {table.id})
            </li>
          ))}
        </ul>
      ) : (
        !isLoadingTables && <p>No tables found for this base.</p>
      )}
      {isLoadingTables && <p>Loading tables...</p>}


      <form onSubmit={handleCreateTable} style={{ marginTop: '2rem', display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={newTableName}
          onChange={(e) => setNewTableName(e.target.value)}
          placeholder="New table name"
          style={{ padding: '0.5rem', flexGrow: 1 }}
        />
        <button type="submit" style={{ padding: '0.5rem 1rem' }}>Create Table</button>
      </form>
      <button onClick={() => navigate('/')} style={{ marginTop: '1rem' }}>Back to Dashboard</button>
    </div>
  );
};

export default BaseDetailPage;
