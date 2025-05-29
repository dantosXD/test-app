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

const getRecordsForTable = async (tableId) => {
  try {
    const response = await apiClient.get(`/tables/${tableId}/records`);
    return response.data;
  } catch (error) {
    console.error('Error fetching records for table:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

// Add other record-related API calls here later (getOne, update, delete)

export default {
  createRecord,
  getRecordsForTable,
};
