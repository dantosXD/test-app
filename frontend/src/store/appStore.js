import { create } from 'zustand';
import tableService from '../services/tableService';
import fieldService from '../services/fieldService';
import recordService from '../services/recordService';
import viewService from '../services/viewService';
import permissionService from '../services/permissionService'; // Import permissionService

const useAppStore = create((set, get) => ({
  // State properties
  currentBaseId: null,
  tables: [],
  currentTableId: null,
  fields: [],
  isLoadingTables: false,
  isLoadingFields: false,
  errorTables: null,
  errorFields: null,
  records: [], // for the current table
  isLoadingRecords: false,
  errorRecords: null,
  currentSort: { fieldId: null, direction: 'asc' },
  currentFilters: { fieldId: null, value: '' },
  views: [], // for current table
  currentViewId: null,
  isLoadingViews: false,
  errorViews: null,
  tablePermissions: [], // For current table
  isLoadingTablePermissions: false,
  errorTablePermissions: null,
  // currentRecord: null, 

  // Actions
  setCurrentBaseId: async (baseId) => {
    if (get().currentBaseId === baseId && get().tables.length > 0 && !get().errorTables) {
      set({ currentBaseId: baseId, currentTableId: null, fields: [], records: [] }); // Clear downstream
      return;
    }
    set({ 
      currentBaseId: baseId, 
      isLoadingTables: true, errorTables: null, tables: [], 
      currentTableId: null, fields: [], records: [] // Clear downstream
    });
    await get().fetchTables(baseId);
  },

  fetchTables: async (baseId) => {
    if (!baseId) {
        set({ tables: [], isLoadingTables: false, errorTables: null, currentTableId: null, fields: [], records: [] });
        return;
    }
    set({ isLoadingTables: true, errorTables: null });
    try {
      const tablesData = await tableService.getTablesForBase(baseId);
      set({ tables: tablesData, isLoadingTables: false });
    } catch (error) {
      console.error('Failed to fetch tables:', error);
      set({ isLoadingTables: false, errorTables: error.message || 'Failed to fetch tables' });
    }
  },

  addTable: async (baseId, tableName) => {
    if (!baseId || !tableName) return;
    try {
      await tableService.createTable(baseId, tableName);
      await get().fetchTables(baseId); // Refresh the list of tables
    } catch (error) {
      console.error('Failed to add table:', error);
      // Optionally set an error state for UI feedback
      set({ errorTables: error.message || 'Failed to add table' });
    }
  },

  setCurrentTableId: async (tableId) => {
    if (get().currentTableId === tableId && get().fields.length > 0 && !get().errorFields && get().records.length > 0 && !get().errorRecords && get().views.length > 0 && !get().errorViews) {
      set({ currentTableId: tableId }); 
      return;
    }
    set({ 
      currentTableId: tableId, 
      isLoadingFields: true, errorFields: null, fields: [], 
      isLoadingRecords: true, errorRecords: null, records: [],
      isLoadingViews: true, errorViews: null, views: [], currentViewId: null, // Reset views
    });
    
    await get().fetchFields(tableId);
    await get().fetchRecords(tableId); 
    await get().fetchViews(tableId); 
    await get().fetchTablePermissions(tableId); // Fetch permissions for the table
  },

  fetchFields: async (tableId) => {
    if (!tableId) {
        set({ fields: [], isLoadingFields: false, errorFields: null, records: [], isLoadingRecords: false, errorRecords: null }); // Clear records too
        return;
    }
    set({ isLoadingFields: true, errorFields: null });
    try {
      const fieldsData = await fieldService.getFieldsForTable(tableId);
      set({ fields: fieldsData, isLoadingFields: false });
    } catch (error) {
      console.error('Failed to fetch fields:', error);
      set({ isLoadingFields: false, errorFields: error.message || 'Failed to fetch fields' });
    }
  },

  addField: async (tableId, fieldData) => {
    if (!tableId || !fieldData) return;
    try {
      await fieldService.createField(tableId, fieldData);
      await get().fetchFields(tableId); // Refresh the list of fields
    } catch (error) {
      console.error('Failed to add field:', error);
      set({ errorFields: error.message || 'Failed to add field' });
    }
  },

  fetchRecords: async (tableId, { sortByFieldId, sortDirection, filterByFieldId, filterValue } = {}) => {
    if (!tableId) {
      set({ records: [], isLoadingRecords: false, errorRecords: null });
      return;
    }
    set({ 
      isLoadingRecords: true, 
      errorRecords: null,
      // Update current sort/filter state if params are provided, otherwise use existing
      currentSort: sortByFieldId !== undefined ? { fieldId: sortByFieldId, direction: sortDirection || 'asc' } : get().currentSort,
      currentFilters: filterByFieldId !== undefined ? { fieldId: filterByFieldId, value: filterValue || ''} : get().currentFilters
    });

    const params = {};
    if (get().currentSort.fieldId !== null) {
        params.sort_by_field_id = get().currentSort.fieldId;
        params.sort_direction = get().currentSort.direction;
    }
    if (get().currentFilters.fieldId !== null && get().currentFilters.value !== '') {
        params.filter_by_field_id = get().currentFilters.fieldId;
        params.filter_value = get().currentFilters.value;
    }

    try {
      const recordsData = await recordService.getRecordsForTable(tableId, params);
      set({ records: recordsData, isLoadingRecords: false });
    } catch (error) {
      console.error('Failed to fetch records:', error);
      set({ isLoadingRecords: false, errorRecords: error.message || 'Failed to fetch records' });
    }
  },
  
  // Action to explicitly set sorting and refetch
  setSort: async (tableId, fieldId, direction) => {
    if (!tableId || fieldId === null) { // Allow clearing sort by passing null fieldId
        set({ currentSort: { fieldId: null, direction: 'asc' }});
    } else {
        set({ currentSort: { fieldId, direction } });
    }
    await get().fetchRecords(tableId); // Refetch with new sort (and existing filters)
  },

  // Action to explicitly set filter and refetch
  setFilter: async (tableId, fieldId, value) => {
     if (!tableId || fieldId === null || value === '') { // Allow clearing filter
        set({ currentFilters: { fieldId: null, value: '' }});
    } else {
        set({ currentFilters: { fieldId, value } });
    }
    await get().fetchRecords(tableId); // Refetch with new filter (and existing sort)
  },


  addRecord: async (tableId, recordData) => {
    if (!tableId || !recordData) return;
    try {
      await recordService.createRecord(tableId, recordData);
      await get().fetchRecords(tableId); // Refresh the list of records
    } catch (error) {
      console.error('Failed to add record:', error);
      set({ errorRecords: error.message || 'Failed to add record' });
    }
  },

  updateRecordValue: async (tableId, recordId, fieldId, newValue) => {
    const currentRecords = get().records;
    const currentFields = get().fields; // Assuming fields are already loaded for the current table
    const recordToUpdate = currentRecords.find(r => r.id === recordId);

    if (!recordToUpdate || !currentFields.length) {
      console.error("Record or fields not found for update");
      set({ errorRecords: "Record or fields not found for update" });
      return;
    }

    // Construct the full 'values' payload as expected by the backend
    // { values: { field_id1: value1, field_id2: value2, ... } }
    const updatedValuesPayload = { values: {} };

    // Populate with existing values first
    recordToUpdate.values.forEach(rv => {
      const fieldDef = currentFields.find(f => f.id === rv.field_id);
      if (fieldDef) {
        // Extract the correct value based on field type (similar to getDisplayValue logic)
        let existingValue;
        switch (fieldDef.type) {
            case 'text': existingValue = rv.value_text; break;
            case 'number': existingValue = rv.value_number; break;
            case 'boolean': existingValue = rv.value_boolean; break;
            case 'date': existingValue = rv.value_datetime; break; // Might need formatting if backend expects string
            default: // singleSelect, multiSelect, email, url, phoneNumber, json types
                existingValue = rv.value_json !== null ? rv.value_json : rv.value_text; 
                break;
        }
        updatedValuesPayload.values[rv.field_id] = existingValue;
      }
    });
    
    // Now, set the new value for the field being updated
    updatedValuesPayload.values[fieldId] = newValue;
    
    try {
      await recordService.updateRecord(recordId, updatedValuesPayload);
      // Refresh records for the current table to show the update
      // This is a simple approach; a more optimized way would be to update the record in the local state directly.
      await get().fetchRecords(tableId); 
    } catch (error) {
      console.error('Failed to update record value:', error);
      set({ errorRecords: error.message || 'Failed to update record value' });
    }
  },

  // Actions to handle WebSocket messages
  handleWebSocketRecordCreated: (newRecord) => {
    set((state) => ({
      records: [...state.records, newRecord],
    }));
  },

  handleWebSocketRecordUpdated: (updatedRecord) => {
    set((state) => ({
      records: state.records.map((record) =>
        record.id === updatedRecord.id ? updatedRecord : record
      ),
    }));
  },

  handleWebSocketRecordDeleted: (deletedRecordData) => { // e.g. { record_id: id, table_id: id }
    set((state) => ({
      records: state.records.filter((record) => record.id !== deletedRecordData.record_id),
    }));
  },
  
  clearRecords: () => {
    set({ records: [], isLoadingRecords: false, errorRecords: null });
  },

  clearCurrentBaseAndTable: () => {
    set({
      currentBaseId: null,
      tables: [],
      currentTableId: null,
      fields: [],
      records: [], // Clear records too
      isLoadingTables: false,
      isLoadingFields: false,
      isLoadingRecords: false,
      errorTables: null,
      errorFields: null,
      errorRecords: null,
      currentSort: { fieldId: null, direction: 'asc' }, 
      currentFilters: { fieldId: null, value: '' },
      views: [], // Reset views state
      currentViewId: null,
      isLoadingViews: false,
      errorViews: null,
      tablePermissions: [], // Reset permissions state
      isLoadingTablePermissions: false,
      errorTablePermissions: null,
    });
  },

  // View Actions
  fetchViews: async (tableId) => {
    if (!tableId) {
        set({ views: [], isLoadingViews: false, errorViews: null, currentViewId: null });
        return;
    }
    set({ isLoadingViews: true, errorViews: null });
    try {
      const viewsData = await viewService.getViewsForTable(tableId);
      set({ views: viewsData, isLoadingViews: false });
    } catch (error) {
      console.error('Failed to fetch views:', error);
      set({ isLoadingViews: false, errorViews: error.message || 'Failed to fetch views' });
    }
  },

  loadView: (viewConfig) => { // viewConfig is the `config` object from a View
    if (!viewConfig) {
        // Reset to default view (e.g., clear sorts, filters, use all fields)
        get().setSort(get().currentTableId, null, 'asc'); // Resets sort
        get().setFilter(get().currentTableId, null, '');   // Resets filter
        // Logic for visible_field_ids and field_order would apply to table column state,
        // which might need to be managed in appStore or TableDetailPage directly.
        // For now, primarily handling sort and filter application.
        set({ currentViewId: null }); // Mark that no specific view is loaded (or a "default" view)
        return;
    }
    
    // Apply sorts from view config
    if (viewConfig.sorts && viewConfig.sorts.length > 0) {
      const firstSort = viewConfig.sorts[0];
      get().setSort(get().currentTableId, firstSort.field_id, firstSort.direction);
    } else {
      get().setSort(get().currentTableId, null, 'asc'); // Clear sort if view has no sorts
    }

    // Apply filters from view config (simplistic: applies first filter if multiple)
    if (viewConfig.filters && viewConfig.filters.length > 0) {
      const firstFilter = viewConfig.filters[0];
      get().setFilter(get().currentTableId, firstFilter.field_id, firstFilter.value);
    } else {
      get().setFilter(get().currentTableId, null, ''); // Clear filter if view has no filters
    }
    
    // Handle visible_field_ids and field_order - this affects column setup in TableDetailPage
    // This might require additional state in appStore or for TableDetailPage to consume this part of config.
    // For now, storing currentViewId and letting TableDetailPage adjust its columns if needed.
    // set({ currentViewConfig: viewConfig }); // Store the whole config if needed
    set(state => ({ 
        ...state, 
        // currentSort and currentFilters are updated by setSort/setFilter calls above
        // Potentially store visible_field_ids and field_order if appStore manages column visibility/order
        // currentVisibleFieldIds: viewConfig.visible_field_ids || null, 
        // currentFieldOrder: viewConfig.field_order || null,
    }));
  },

  saveCurrentView: async (tableId, viewName, currentGridConfig, viewIdToUpdate = null) => {
    if (!tableId || !viewName || !currentGridConfig) {
        console.error("Missing data for saving view");
        set({ errorViews: "Missing data for saving view" });
        return;
    }
    const viewPayload = {
        name: viewName,
        config: currentGridConfig, // { visible_field_ids, field_order, sorts, filters }
    };
    try {
        if (viewIdToUpdate) {
            await viewService.updateView(viewIdToUpdate, viewPayload);
        } else {
            await viewService.createTableView(tableId, viewPayload);
        }
        await get().fetchViews(tableId); // Refresh views list
        set({ errorViews: null });
    } catch (error) {
        console.error('Failed to save view:', error);
        set({ errorViews: error.message || 'Failed to save view' });
        throw error; // Re-throw for form handling
    }
  },

  deleteView: async (tableId, viewId) => {
    if (!viewId) return;
    try {
        await viewService.deleteView(viewId);
        await get().fetchViews(tableId); // Refresh views list
        if (get().currentViewId === viewId) { // If current view deleted, load default
            get().loadView(null); 
            set({ currentViewId: null });
        }
        set({ errorViews: null });
    } catch (error) {
        console.error('Failed to delete view:', error);
        set({ errorViews: error.message || 'Failed to delete view' });
    }
  },

  // Table Permissions Actions
  fetchTablePermissions: async (tableId) => {
    if (!tableId) {
        set({ tablePermissions: [], isLoadingTablePermissions: false, errorTablePermissions: null });
        return;
    }
    set({ isLoadingTablePermissions: true, errorTablePermissions: null });
    try {
      const permissions = await permissionService.getTablePermissions(tableId);
      set({ tablePermissions: permissions, isLoadingTablePermissions: false });
    } catch (error) {
      console.error('Failed to fetch table permissions:', error);
      set({ isLoadingTablePermissions: false, errorTablePermissions: error.message || 'Failed to fetch permissions' });
    }
  },

  grantPermission: async (tableId, userEmail, permissionLevel) => {
    if (!tableId || !userEmail || !permissionLevel) return;
    try {
      await permissionService.grantTablePermission(tableId, userEmail, permissionLevel);
      await get().fetchTablePermissions(tableId); // Refresh list
      set({ errorTablePermissions: null });
    } catch (error) {
      console.error('Failed to grant permission:', error);
      set({ errorTablePermissions: error.message || 'Failed to grant permission' });
      throw error; // Re-throw for form handling
    }
  },

  revokePermission: async (tableId, targetUserId) => {
    if (!tableId || !targetUserId) return;
    try {
      await permissionService.revokeTablePermission(tableId, targetUserId);
      await get().fetchTablePermissions(tableId); // Refresh list
      set({ errorTablePermissions: null });
    } catch (error) {
      console.error('Failed to revoke permission:', error);
      set({ errorTablePermissions: error.message || 'Failed to revoke permission' });
      throw error;
    }
  }

}));
}));

export default useAppStore;
