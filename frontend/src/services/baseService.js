import apiClient from './api';

const getBases = async () => {
  try {
    const response = await apiClient.get('/bases/'); // Note: backend might have trailing slash or not. Adjust as needed.
    return response.data;
  } catch (error) {
    console.error('Error fetching bases:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

// Add other base-related API calls here later (create, update, delete)
// e.g.,
// const createBase = async (baseData) => {
//   try {
//     const response = await apiClient.post('/bases/', baseData);
//     return response.data;
//   } catch (error) {
//     console.error('Error creating base:', error.response?.data || error.message);
//     throw error.response?.data || error.message;
//   }
// };

export default {
  getBases,
  // createBase, 
};
