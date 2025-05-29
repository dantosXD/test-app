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
};
