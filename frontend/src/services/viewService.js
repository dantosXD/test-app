import apiClient from './api';

const createTableView = async (tableId, viewData) => {
  // viewData: { name: string, config: object }
  try {
    const response = await apiClient.post(`/tables/${tableId}/views`, viewData);
    return response.data;
  } catch (error) {
    console.error('Error creating view:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const getViewsForTable = async (tableId) => {
  try {
    const response = await apiClient.get(`/tables/${tableId}/views`);
    return response.data;
  } catch (error) {
    console.error('Error fetching views for table:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const getViewDetails = async (viewId) => {
  try {
    const response = await apiClient.get(`/views/${viewId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching view details:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const updateView = async (viewId, viewData) => {
  // viewData: { name?: string, config?: object }
  try {
    const response = await apiClient.put(`/views/${viewId}`, viewData);
    return response.data;
  } catch (error) {
    console.error('Error updating view:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const deleteView = async (viewId) => {
  try {
    await apiClient.delete(`/views/${viewId}`);
  } catch (error) {
    console.error('Error deleting view:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

export default {
  createTableView,
  getViewsForTable,
  getViewDetails,
  updateView,
  deleteView,
};
