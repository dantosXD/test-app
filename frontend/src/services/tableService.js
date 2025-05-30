import apiClient from './api';

const createTable = async (baseId, tableName) => {
  try {
    const response = await apiClient.post(`/bases/${baseId}/tables`, { name: tableName });
    return response.data;
  } catch (error) {
    console.error('Error creating table:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const getTablesForBase = async (baseId) => {
  try {
    const response = await apiClient.get(`/bases/${baseId}/tables`);
    return response.data;
  } catch (error) {
    console.error('Error fetching tables for base:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

// Add other table-related API calls here later (getOne, update, delete)

export default {
  createTable,
  getTablesForBase,
  // Note: getRecordsForTable, createRecord, updateRecord are in recordService.js

  // For CSV Export, we just need the URL. The browser will handle the download.
  getExportCsvUrl: (tableId) => {
    // Assumes apiClient.defaults.baseURL is set, e.g., "http://localhost:8000"
    // Or construct full URL if needed: `${apiClient.defaults.baseURL}/tables/${tableId}/export_csv`
    // However, for direct link, we need to ensure auth token is handled if endpoint is protected.
    // The backend endpoint /tables/{table_id}/export_csv has `Depends(auth.get_current_active_user)`.
    // Direct browser navigation won't include Authorization header.
    // A solution is to fetch the blob via JS and then trigger download, or temp token in URL (less secure).
    // For now, let's return the relative URL and handle fetch-then-download in the component.
    return `/tables/${tableId}/export_csv`;
  },

  importCsv: async (tableId, fileObject, onUploadProgress) => {
    const formData = new FormData();
    formData.append('file', fileObject);
    try {
      const response = await apiClient.post(`/tables/${tableId}/import_csv`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress,
      });
      return response.data; // { success_count, error_count, errors }
    } catch (error) {
      console.error(`Error importing CSV for table ${tableId}:`, error.response?.data || error.message);
      throw error.response?.data || error.message;
    }
  },
};
