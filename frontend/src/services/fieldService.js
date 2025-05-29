import apiClient from './api';

const createField = async (tableId, fieldData) => {
  // fieldData should be an object like { name: "New Field", type: "text", options: {} }
  try {
    const response = await apiClient.post(`/tables/${tableId}/fields`, fieldData);
    return response.data;
  } catch (error) {
    console.error('Error creating field:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const getFieldsForTable = async (tableId) => {
  try {
    const response = await apiClient.get(`/tables/${tableId}/fields`);
    return response.data;
  } catch (error) {
    console.error('Error fetching fields for table:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

// Add other field-related API calls here later (getOne, update, delete)

export default {
  createField,
  getFieldsForTable,
};
