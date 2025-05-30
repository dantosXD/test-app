import apiClient from './api'; // Uses the existing configured Axios instance

const getPublicFormConfig = async (viewId) => {
  try {
    const response = await apiClient.get(`/public/forms/${viewId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching public form config for view ${viewId}:`, error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const submitPublicForm = async (viewId, data) => {
  // data is an object like { "field_X_id": "value", ... }
  try {
    const response = await apiClient.post(`/public/forms/${viewId}`, data);
    return response.data; // Should include { message: "...", record_id: ... }
  } catch (error) {
    console.error(`Error submitting public form for view ${viewId}:`, error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

export default {
  getPublicFormConfig,
  submitPublicForm,
};
