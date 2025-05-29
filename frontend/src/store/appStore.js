import { create } from 'zustand';
import tableService from '../services/tableService';
import fieldService from '../services/fieldService';
import recordService from '../services/recordService'; // Import recordService

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
  // currentRecord: null, // Optional for later

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
    if (get().currentTableId === tableId && get().fields.length > 0 && !get().errorFields && get().records.length > 0 && !get().errorRecords) {
      set({ currentTableId: tableId }); // Avoid refetch if already current and data is loaded
      return;
    }
    set({ currentTableId: tableId, isLoadingFields: true, errorFields: null, fields: [], isLoadingRecords: true, errorRecords: null, records: [] });
    // Fetch fields and records in parallel or sequentially
    await get().fetchFields(tableId);
    await get().fetchRecords(tableId); // Also fetch records
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

  fetchRecords: async (tableId) => {
    if (!tableId) {
      set({ records: [], isLoadingRecords: false, errorRecords: null });
      return;
    }
    set({ isLoadingRecords: true, errorRecords: null });
    try {
      const recordsData = await recordService.getRecordsForTable(tableId);
      set({ records: recordsData, isLoadingRecords: false });
    } catch (error) {
      console.error('Failed to fetch records:', error);
      set({ isLoadingRecords: false, errorRecords: error.message || 'Failed to fetch records' });
    }
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
    });
  },
}));

export default useAppStore;
