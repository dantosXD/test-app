import apiClient from './api';
import useAuthStore from '../store/authStore';

const register = async (email, password) => {
  try {
    const response = await apiClient.post('/auth/register', { email, password });
    return response.data;
  } catch (error) {
    console.error('Registration error:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const login = async (email, password) => {
  try {
    // FastAPI's OAuth2PasswordRequestForm expects form data
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const { access_token, token_type } = response.data;
    if (access_token) {
      // For now, user data is not returned by /auth/login in the backend.
      // We'll set a minimal user object or fetch it separately.
      // Let's assume email is the user identifier for now.
      // A proper /users/me endpoint would be better to get full user data.
      // The backend's /auth/users/me can be used after login.
      useAuthStore.getState().login(access_token, { email }); // Store token and basic user info

      // Fetch full user details after successful login
      try {
        const userDetailsResponse = await apiClient.get('/auth/users/me'); // uses the token via interceptor
        useAuthStore.getState().setUser(userDetailsResponse.data); // Update user state with full details
      } catch (userError) {
        console.error('Error fetching user details after login:', userError.response?.data || userError.message);
        // Decide if login should fail or proceed with minimal user data
        // For now, proceed, user data will be minimal.
      }

    }
    return response.data;
  } catch (error) {
    console.error('Login error:', error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const logout = () => {
  useAuthStore.getState().logout();
  // Potentially call a backend logout endpoint if it exists
};

// Example: Function to get current user details (if needed outside of login)
const getCurrentUser = async () => {
    if (!useAuthStore.getState().isAuthenticated) {
        return null;
    }
    try {
        const response = await apiClient.get('/auth/users/me');
        useAuthStore.getState().setUser(response.data);
        return response.data;
    } catch (error) {
        console.error('Error fetching current user:', error.response?.data || error.message);
        // If token is invalid (e.g. 401), logout user
        if (error.response?.status === 401) {
            logout();
        }
        throw error.response?.data || error.message;
    }
}


export default {
  register,
  login,
  logout,
  getCurrentUser,
};
