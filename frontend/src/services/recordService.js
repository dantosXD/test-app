import apiClient from './api';

const createRecord = async (tableId, recordData) => {
  // recordData should be an object like { values: { field_id1: value1, field_id2: value2 } }
  try {
    const response = await apiClient.post(`/tables/${tableId}/records`, recordData);
    return response.data;
  } catch (error) {
    console.error('Error creating record:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const getRecordsForTable = async (tableId, params = {}) => {
  // params: { sortByFieldId, sortDirection, filterByFieldId, filterValue }
  try {
    const response = await apiClient.get(`/tables/${tableId}/records`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching records for table:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const updateRecord = async (recordId, recordData) => {
  // recordData should be an object like { values: { field_id1: value1, field_id2: value2 } }
  // or whatever the backend PUT /records/{record_id} expects.
  // Based on backend implementation, it expects RecordUpdate schema: { values: Optional[dict[int, Any]] }
  try {
    const response = await apiClient.put(`/records/${recordId}`, recordData);
    return response.data;
  } catch (error) {
    console.error('Error updating record:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

// Add other record-related API calls here later (getOne, delete)

export default {
  createRecord,
  getRecordsForTable,
  updateRecord, // Add new function to export
};
