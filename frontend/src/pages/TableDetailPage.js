import React, { useEffect, useState, useMemo, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import useAppStore from '../store/appStore';
import { useReactTable, getCoreRowModel, flexRender } from '@tanstack/react-table';
import EditableCell from '../components/EditableCell';
import useWebSocket from '../hooks/useWebSocket';
import KanbanBoard from '../components/KanbanView/KanbanBoard';
import CalendarViewComponent from '../components/CalendarView/CalendarView';
import GalleryViewComponent from '../components/GalleryView/GalleryView';
import fileService from '../services/fileService';
import tableService from '../services/tableService'; // For CSV import/export
import apiClient from '../services/api'; // For direct blob fetch for export

const TableDetailPage = () => {
  const { tableId } = useParams();
  const navigate = useNavigate();
  const store = useAppStore();
  const { /* ... existing store destructuring ... */
    currentTableId, fields, isLoadingFields, errorFields, records, isLoadingRecords, errorRecords,
    setCurrentTableId, addField, addRecord, updateRecordValue, currentBaseId,
    handleWebSocketRecordCreated, handleWebSocketRecordUpdated, handleWebSocketRecordDeleted,
    currentSort, currentFilters, setSort, setFilter,
    views, currentViewId, isLoadingViews, errorViews, loadView, saveCurrentView, deleteView,
    tablePermissions, fetchRecords // Added fetchRecords for re-fetching after import
  } = store;

  const tableName = `Table ${tableId}`;

  // ... (all other state variables as before) ...
  const [newFieldName, setNewFieldName] = useState(''); /* ... */
  const [showImportCsvModal, setShowImportCsvModal] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importResults, setImportResults] = useState(null);
  const [isImporting, setIsImporting] = useState(false);


  const fieldTypes = [ /* ... */ ];
  const viewTypesForSelect = ['grid', 'form', 'kanban', 'calendar', 'gallery'];
  const kanbanCompatibleFieldTypes = [/* ... */];
  const dateCompatibleFieldTypes = [/* ... */];
  const attachmentCompatibleFieldTypes = ['attachment'];

  // --- Callbacks and Effects (mostly unchanged) ---
  const handleWebSocketMessage = useCallback((message) => { /* ... */ }, [/* ... */]);
  const { isConnected: wsIsConnected, error: wsError } = useWebSocket(currentTableId ? tableId : null, handleWebSocketMessage);
  useEffect(() => { /* ... setCurrentTableId logic ... */ }, [/* ... */]);
  const currentLoadedView = useMemo(() => views.find(v => v.id === currentViewId), [currentViewId, views]);
  useEffect(() => { /* ... loadView logic ... */ }, [/* ... */]);
  const columns = useMemo(() => { /* ... */ }, [/* ... */]);
  const tableData = useMemo(() => { /* ... */ }, [records, fields]);
  const table = useReactTable({ data: tableData, columns, getCoreRowModel: getCoreRowModel(), meta: { apiBaseUrl: "http://localhost:8000", updateData: (recordId, fieldId, value) => { /* ... */ }}});
  const handleCreateField = async (e) => { /* ... */ };
  const handleNewRecordInputChange = (fieldId, value, fieldType) => { /* ... */ };
  const handleCreateRecord = async (e) => { /* ... */ };
  const handleSaveView = async () => { /* ... */ };
  const openSaveViewModal = () => { /* ... */ };
  const handleGrantPermission = async () => { /* ... */ };
  const handleRevokePermission = async (targetUserId) => { /* ... */ };

  const handleExportCsv = async () => {
    if (!currentTableId) return;
    try {
        const exportUrl = tableService.getExportCsvUrl(currentTableId);
        // Fetch the CSV data using apiClient to include auth headers
        const response = await apiClient.get(exportUrl, { responseType: 'blob' });
        const blob = new Blob([response.data], { type: 'text/csv' });
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        // Extract filename from content-disposition header if possible, otherwise default
        const contentDisposition = response.headers['content-disposition'];
        let filename = `table_${currentTableId}_export.csv`;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
            if (filenameMatch && filenameMatch.length === 2)
                filename = filenameMatch[1];
        }
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
        console.error("Error exporting CSV:", error);
        alert("Failed to export CSV. See console for details.");
    }
  };

  const handleImportCsvFileSelect = (event) => {
    setImportFile(event.target.files[0]);
    setImportResults(null); // Clear previous results
  };

  const handleStartImportCsv = async () => {
    if (!importFile || !currentTableId) {
        alert("Please select a CSV file to import.");
        return;
    }
    setIsImporting(true);
    setImportResults(null);
    try {
        const results = await tableService.importCsv(currentTableId, importFile);
        setImportResults(results);
        if (results.success_count > 0) {
            fetchRecords(currentTableId); // Refresh records if import was successful
        }
    } catch (error) {
        setImportResults({ message: "Import failed.", errors: [ {error: error.message || "Unknown error"} ], success_count: 0, error_count: 'N/A' });
    } finally {
        setIsImporting(false);
    }
  };


  if ((isLoadingFields && fields.length === 0) || (isLoadingRecords && records.length === 0 && !errorRecords && (!currentLoadedView || !['form', 'kanban', 'calendar', 'gallery'].includes(currentLoadedView.type) ) )) { /* ... */ }
  if (errorFields) { /* ... */ }

  return (
    <div className="container" style={{ padding: '2rem' }}>
      {/* ... Header, Fields Definition, Add New Field Form ... */}

      {/* View Management UI - Add Export/Import buttons */}
      <div style={{ margin: '1rem 0', padding: '1rem', border: '1px solid #ddd', borderRadius: '5px', backgroundColor: '#f9f9f9' }}>
        {/* ... existing View Management content (dropdown, save/delete view, permissions) ... */}
        <div style={{marginTop:'10px', paddingTop:'10px', borderTop: '1px solid #eee', display:'flex', gap:'10px'}}>
            <button onClick={handleExportCsv} style={{padding: '0.5rem'}}>Export CSV</button>
            <button onClick={() => { setShowImportCsvModal(true); setImportFile(null); setImportResults(null); }} style={{padding: '0.5rem'}}>Import CSV</button>
        </div>
      </div>

      {/* ... Save View Modal ... */}
      {/* ... Permissions Modal ... */}

      {/* Import CSV Modal */}
      {showImportCsvModal && (
        <div style={{ position: 'fixed', top: '20%', left: '50%', transform: 'translate(-50%, -20%)', backgroundColor: 'white', padding: '20px', border: '1px solid #ccc', zIndex: 1050, boxShadow: '0 2px 10px rgba(0,0,0,0.1)', width: '500px'}}>
            <h4>Import CSV to {tableName}</h4>
            <input type="file" accept=".csv" onChange={handleImportCsvFileSelect} style={{display:'block', marginBottom:'15px'}} />
            <button onClick={handleStartImportCsv} disabled={!importFile || isImporting} style={{marginRight:'10px'}}>
                {isImporting ? 'Importing...' : 'Start Import'}
            </button>
            <button onClick={() => setShowImportCsvModal(false)} style={{backgroundColor:'#6c757d'}}>Close</button>
            {importResults && (
                <div style={{marginTop:'15px', maxHeight:'200px', overflowY:'auto', border:'1px solid #eee', padding:'10px'}}>
                    <p>{importResults.message}</p>
                    {importResults.errors && importResults.errors.length > 0 && (
                        <>
                            <p><strong>Errors:</strong></p>
                            <ul style={{fontSize:'0.9em', color:'red'}}>
                                {importResults.errors.slice(0, 10).map((err, idx) => ( // Show first 10 errors
                                    <li key={idx}>{err.row ? `Row ${err.row}: ` : ''}{err.error || JSON.stringify(err)}</li>
                                ))}
                                {importResults.errors.length > 10 && <li>...and {importResults.errors.length - 10} more errors.</li>}
                            </ul>
                        </>
                    )}
                </div>
            )}
        </div>
      )}

      {/* Conditional rendering for Grid, Form, Kanban or Calendar View Info */}
      {/* ... */}
      {/* Add New Record Form (conditionally hidden) */}
      {/* ... */}
    </div>
  );
};
export default TableDetailPage;
