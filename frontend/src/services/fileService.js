import apiClient from './api';

const uploadFile = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await apiClient.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress, // Pass progress callback to axios
    });
    return response.data; // { filename, original_filename, content_type, size, url }
  } catch (error) {
    console.error('Error uploading file:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

export default {
  uploadFile,
};
