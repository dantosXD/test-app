import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import useAppStore from '../store/appStore';

const TableDetailPage = () => {
  const { tableId } = useParams();
  const navigate = useNavigate();

  const {
    currentTableId,
    fields,
    isLoadingFields,
    errorFields,
    records, // new state
    isLoadingRecords, // new state
    errorRecords, // new state
    setCurrentTableId,
    addField,
    addRecord, // new action
    currentBaseId, 
  } = useAppStore();

  const tableName = `Table ${tableId}`; 

  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldType, setNewFieldType] = useState('text'); 
  const [newRecordData, setNewRecordData] = useState({}); // For the new record form

  const fieldTypes = [
    'text', 'number', 'date', 'boolean', 'singleSelect', 'multiSelect', 
    'email', 'url', 'phoneNumber'
  ];

  useEffect(() => {
    const numTableId = parseInt(tableId);
    if (isNaN(numTableId)) {
        navigate(currentBaseId ? `/bases/${currentBaseId}` : '/'); 
        return;
    }
    if (currentTableId !== numTableId || fields.length === 0 || records.length === 0) { // Condition to also fetch if records are empty
        setCurrentTableId(numTableId); // This now fetches fields and records
    }
  }, [tableId, currentTableId, fields.length, records.length, setCurrentTableId, navigate, currentBaseId]);

  const handleCreateField = async (e) => {
    e.preventDefault();
    if (!newFieldName.trim() || !newFieldType.trim()) return;
    await addField(parseInt(tableId), { name: newFieldName, type: newFieldType });
    setNewFieldName('');
    setNewFieldType('text');
  };

  const handleNewRecordInputChange = (fieldId, value) => {
    setNewRecordData(prev => ({ ...prev, [fieldId]: value }));
  };

  const handleCreateRecord = async (e) => {
    e.preventDefault();
    if (Object.keys(newRecordData).length === 0) {
        alert("Please enter data for at least one field.");
        return;
    }
    // Ensure all values are appropriately typed if necessary, though backend handles some conversion
    const recordPayload = { values: {} };
    for (const fieldIdStr in newRecordData) {
        const fieldId = parseInt(fieldIdStr);
        const field = fields.find(f => f.id === fieldId);
        if (field) {
            let value = newRecordData[fieldIdStr];
            // Basic type conversion based on field type for better data integrity
            if (field.type === 'number') value = parseFloat(value) || null;
            if (field.type === 'boolean') value = Boolean(value);
            // Dates would need more careful handling if not using a date picker
            recordPayload.values[fieldId] = value;
        }
    }
    await addRecord(parseInt(tableId), recordPayload);
    setNewRecordData({}); // Clear form
  };
  
  // Helper to get the actual value from a RecordValue object based on field type
  const getDisplayValue = (recordValue, fieldType) => {
    if (!recordValue) return 'N/A';
    switch (fieldType) {
      case 'text': return recordValue.value_text;
      case 'number': return recordValue.value_number;
      case 'boolean': return recordValue.value_boolean !== null ? String(recordValue.value_boolean) : 'N/A';
      case 'date': return recordValue.value_datetime ? new Date(recordValue.value_datetime).toLocaleDateString() : 'N/A';
      case 'singleSelect': // Assuming stored in value_text or value_json
      case 'multiSelect':
      case 'attachment':
      case 'email':
      case 'url':
      case 'phoneNumber':
        return recordValue.value_text || (recordValue.value_json ? JSON.stringify(recordValue.value_json) : 'N/A');
      default:
        return recordValue.value_text || recordValue.value_number || String(recordValue.value_boolean) || recordValue.value_datetime || (recordValue.value_json ? JSON.stringify(recordValue.value_json) : 'N/A');
    }
  };


  if (isLoadingFields && fields.length === 0) {
    return <div className="container">Loading table details for {tableName}...</div>;
  }
  if (errorFields) {
    return <div className="container" style={{ color: 'red' }}>Error loading fields: {errorFields}</div>;
  }

  return (
    <div className="container" style={{ padding: '2rem' }}>
      <h2>{tableName}</h2>
      <p><Link to={currentBaseId ? `/bases/${currentBaseId}` : '/'}>Back to Base</Link></p>
      
      <h3 style={{marginTop: '2rem'}}>Fields:</h3>
      {fields.length > 0 ? (
        <ul style={{ listStyle: 'none', padding: 0, display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {fields.map((field) => (
            <li 
              key={field.id}
              style={{ 
                padding: '8px', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#eee',
                fontSize: '0.9em'
              }}
            >
              <strong>{field.name}</strong> ({field.type})
            </li>
          ))}
        </ul>
      ) : (
         !isLoadingFields && <p>No fields found for this table. Add fields below.</p>
      )}
      {isLoadingFields && <p>Loading fields...</p>}

      <form onSubmit={handleCreateField} style={{ marginTop: '1rem', marginBottom: '2rem', border: '1px solid #eee', padding: '1rem', borderRadius: '5px' }}>
        <h4>Add New Field</h4>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
          <input
            type="text"
            value={newFieldName}
            onChange={(e) => setNewFieldName(e.target.value)}
            placeholder="New field name"
            style={{ padding: '0.5rem', flexGrow: 1 }}
            required
          />
          <select 
            value={newFieldType} 
            onChange={(e) => setNewFieldType(e.target.value)}
            style={{ padding: '0.5rem' }}
            required
          >
            {fieldTypes.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
        </div>
        <button type="submit" style={{ padding: '0.5rem 1rem' }}>Create Field</button>
      </form>

      <hr style={{margin: "2rem 0"}}/>

      <h3>Records:</h3>
      {isLoadingRecords && <p>Loading records...</p>}
      {errorRecords && <p style={{color: 'red'}}>Error loading records: {errorRecords}</p>}
      
      {!isLoadingRecords && records.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          {records.map(record => (
            <div key={record.id} style={{ border: '1px solid #ddd', padding: '1rem', marginBottom: '1rem', borderRadius: '5px' }}>
              <h4>Record ID: {record.id}</h4>
              {record.values.map(rv => {
                const fieldDef = fields.find(f => f.id === rv.field_id);
                return (
                  <div key={rv.id} style={{ marginLeft: '10px', fontSize: '0.9em' }}>
                    <strong>{fieldDef ? fieldDef.name : `Field ID ${rv.field_id}`}: </strong> 
                    {getDisplayValue(rv, fieldDef ? fieldDef.type : 'unknown')}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}
      {!isLoadingRecords && records.length === 0 && !errorRecords && (
        <p>No records yet in this table.</p>
      )}

      <form onSubmit={handleCreateRecord} style={{ marginTop: '1rem', border: '1px solid #eee', padding: '1rem', borderRadius: '5px' }}>
        <h4>Add New Record</h4>
        {fields.length === 0 ? <p>Please add fields to the table before creating records.</p> : (
          fields.map(field => (
            <div key={field.id} style={{ marginBottom: '0.5rem' }}>
              <label htmlFor={`record-field-${field.id}`} style={{ marginRight: '0.5rem', display: 'inline-block', width: '120px' }}>
                {field.name} ({field.type}):
              </label>
              <input
                type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text'}
                id={`record-field-${field.id}`}
                value={newRecordData[field.id] || ''}
                onChange={(e) => handleNewRecordInputChange(field.id, e.target.value)}
                style={{ padding: '0.3rem' }}
              />
            </div>
          ))
        )}
        {fields.length > 0 && <button type="submit" style={{ padding: '0.5rem 1rem', marginTop: '0.5rem' }}>Create Record</button>}
      </form>

      <button onClick={() => navigate(currentBaseId ? `/bases/${currentBaseId}` : '/')} style={{ marginTop: '2rem' }}>
        Back to Base Details
      </button>
    </div>
  );
};

export default TableDetailPage;
