import apiClient from './api';

const getTablePermissions = async (tableId) => {
  try {
    const response = await apiClient.get(`/tables/${tableId}/permissions`);
    return response.data; // Expected: List[TablePermissionResponse]
  } catch (error) {
    console.error(`Error fetching permissions for table ${tableId}:`, error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const grantTablePermission = async (tableId, userEmail, permissionLevel) => {
  try {
    const response = await apiClient.post(`/tables/${tableId}/permissions`, {
      user_email: userEmail,
      permission_level: permissionLevel,
    });
    return response.data; // Expected: TablePermissionResponse
  } catch (error) {
    console.error(`Error granting permission for table ${tableId} to ${userEmail}:`, error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

const revokeTablePermission = async (tableId, targetUserId) => {
  try {
    await apiClient.delete(`/tables/${tableId}/permissions/${targetUserId}`);
  } catch (error) {
    console.error(`Error revoking permission for table ${tableId} from user ${targetUserId}:`, error.response?.data || error.message);
    throw error.response?.data || error.message;
  }
};

export default {
  getTablePermissions,
  grantTablePermission,
  revokeTablePermission,
};
