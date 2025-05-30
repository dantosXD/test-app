import React, { useState, useEffect, useMemo } from 'react';
import { DndContext, closestCorners, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { arrayMove, SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import useAppStore from '../../store/appStore';
import KanbanColumn from './KanbanColumn';

const KanbanBoard = ({ records: initialRecords, viewConfig }) => {
  const { fields, updateRecordValue, currentTableId } = useAppStore();
  
  const stackByField = useMemo(() => fields.find(f => f.id === viewConfig.stack_by_field_id), [fields, viewConfig.stack_by_field_id]);

  // State for tasks, organized by column ID. This needs to be derived from initialRecords and viewConfig.
  const [tasksByColumnId, setTasksByColumnId] = useState({});

  // This effect will re-calculate tasksByColumnId when initialRecords, stackByField, or viewConfig changes.
  useEffect(() => {
    if (!stackByField) {
      // Handle case where stackByField is not found or invalid
      const uncategorized = { id: "uncategorized", title: "Uncategorized", records: initialRecords.map(r => ({ ...r, id: String(r.id) })) };
      setTasksByColumnId({ "uncategorized": uncategorized.records });
      return;
    }

    let columnKeys = [];
    if (viewConfig.column_order && viewConfig.column_order.length > 0) {
      columnKeys = viewConfig.column_order;
    } else if (stackByField.type === 'singleSelect' && stackByField.options?.choices) {
      columnKeys = stackByField.options.choices;
    } else {
      const uniqueValues = new Set();
      initialRecords.forEach(record => {
        const recordValueContainer = record.values.find(rv => rv.field_id === stackByField.id);
        let value = null;
        if (recordValueContainer) {
          if (stackByField.type === 'text' || stackByField.type === 'singleSelect') value = recordValueContainer.value_text;
          else if (stackByField.type === 'boolean') value = recordValueContainer.value_boolean !== null ? String(recordValueContainer.value_boolean) : null;
        }
        uniqueValues.add(value !== null && value !== undefined && String(value).trim() !== "" ? String(value) : "Uncategorized");
      });
      columnKeys = Array.from(uniqueValues);
    }
    
    // Ensure "Uncategorized" is an option if records might fall into it
    const hasUncategorizedPotential = initialRecords.some(record => {
        const recordValueContainer = record.values.find(rv => rv.field_id === stackByField.id);
        let value = null;
        if (recordValueContainer) {
            if (stackByField.type === 'text' || stackByField.type === 'singleSelect') value = recordValueContainer.value_text;
            else if (stackByField.type === 'boolean') value = recordValueContainer.value_boolean !== null ? String(recordValueContainer.value_boolean) : null;
        }
        return value === null || value === undefined || String(value).trim() === "";
    });

    if (hasUncategorizedPotential && !columnKeys.includes("Uncategorized")) {
        columnKeys.push("Uncategorized");
    }
    if (columnKeys.length === 0 && initialRecords.length > 0) { // If no columns from config/choices and records exist
        columnKeys.push("Uncategorized");
    }


    const newTasksByColumnId = {};
    columnKeys.forEach(key => newTasksByColumnId[String(key)] = []);

    initialRecords.forEach(record => {
      const recordValueContainer = record.values.find(rv => rv.field_id === stackByField.id);
      let columnKeyValue = "Uncategorized";
      if (recordValueContainer) {
        let rawValue = null;
        if (stackByField.type === 'text' || stackByField.type === 'singleSelect') rawValue = recordValueContainer.value_text;
        else if (stackByField.type === 'boolean') rawValue = recordValueContainer.value_boolean !== null ? String(recordValueContainer.value_boolean) : null;
        
        if (rawValue !== null && rawValue !== undefined && String(rawValue).trim() !== "") {
            columnKeyValue = String(rawValue);
        }
      }
      if (newTasksByColumnId[columnKeyValue]) {
        newTasksByColumnId[columnKeyValue].push({ ...record, id: String(record.id) });
      } else if (newTasksByColumnId["Uncategorized"]) { // Fallback if a value is not in columnKeys
        newTasksByColumnId["Uncategorized"].push({ ...record, id: String(record.id) });
      }
    });
    setTasksByColumnId(newTasksByColumnId);
  }, [initialRecords, stackByField, viewConfig.column_order, fields]);


  const orderedColumnIds = useMemo(() => {
    if (!stackByField) return ["uncategorized"];
    let order = [];
    if (viewConfig.column_order && viewConfig.column_order.length > 0) {
      order = viewConfig.column_order;
    } else if (stackByField.options?.choices) {
      order = stackByField.options.choices;
    } else {
      order = Object.keys(tasksByColumnId); // Fallback to keys from processed tasks
    }
    // Ensure "Uncategorized" column is present if it has tasks or was implicitly added
    if (tasksByColumnId["Uncategorized"]?.length > 0 && !order.includes("Uncategorized")) {
        order.push("Uncategorized");
    } else if (order.length === 0 && tasksByColumnId["Uncategorized"]?.length >=0 ) { // if no order and uncategorized exists
        order = ["Uncategorized"];
    }
    return order.map(String); // Ensure string IDs
  }, [stackByField, viewConfig.column_order, tasksByColumnId]);


  const sensors = useSensors(useSensor(PointerSensor));

  const handleDragEnd = (event) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = String(active.id); // ID of the dragged card (record.id)
    const overId = String(over.id);   // ID of the droppable area (columnId) or another card

    setTasksByColumnId((prevTasks) => {
      let newTasks = { ...prevTasks };
      let sourceColumnId = null;
      let activeItem = null;

      // Find the source column and the active item
      for (const colId in newTasks) {
        const itemIndex = newTasks[colId].findIndex(task => String(task.id) === activeId);
        if (itemIndex !== -1) {
          sourceColumnId = colId;
          activeItem = newTasks[colId][itemIndex];
          break;
        }
      }

      if (!activeItem) return prevTasks; // Should not happen

      // Determine the target column
      // over.id could be a column ID or an item ID (if dropped on an item)
      let targetColumnId = null;
      if (newTasks[overId]) { // Dropped directly onto a column
        targetColumnId = overId;
      } else { // Dropped onto an item, find that item's column
        for (const colId in newTasks) {
          if (newTasks[colId].find(task => String(task.id) === overId)) {
            targetColumnId = colId;
            break;
          }
        }
      }
      
      if (!targetColumnId) return prevTasks; // Should not happen if over a valid droppable

      if (sourceColumnId === targetColumnId) {
        // Reorder within the same column
        const itemIndexInSource = newTasks[sourceColumnId].findIndex(task => String(task.id) === activeId);
        let itemIndexInOver = newTasks[targetColumnId].findIndex(task => String(task.id) === overId);
        // If overId is the column itself (not an item), itemIndexInOver might be -1. Place at end.
        if (overId === targetColumnId && itemIndexInOver === -1) itemIndexInOver = newTasks[targetColumnId].length -1 ;


        if (itemIndexInSource !== -1 && itemIndexInOver !== -1) {
            newTasks[sourceColumnId] = arrayMove(newTasks[sourceColumnId], itemIndexInSource, itemIndexInOver);
        }
      } else {
        // Move to a different column
        const sourceItems = [...newTasks[sourceColumnId]];
        const destItems = [...newTasks[targetColumnId]];
        const activeIndexInSource = sourceItems.findIndex(t => String(t.id) === activeId);
        
        // Remove from source
        sourceItems.splice(activeIndexInSource, 1);
        
        // Add to destination (at specific index if dropped on item, else at end)
        let destIndex = destItems.length; // Default to end
        const overItemIndexInDest = destItems.findIndex(t => String(t.id) === overId);
        if (overItemIndexInDest !== -1) {
            destIndex = overItemIndexInDest;
        }

        destItems.splice(destIndex, 0, activeItem);
        
        newTasks = { ...newTasks, [sourceColumnId]: sourceItems, [targetColumnId]: destItems };

        // Update backend
        const recordId = parseInt(activeId);
        let newStackValue = targetColumnId;
        if (stackByField.type === 'boolean') {
          if (targetColumnId.toLowerCase() === 'true') newStackValue = true;
          else if (targetColumnId.toLowerCase() === 'false') newStackValue = false;
          else newStackValue = null;
        } else if (targetColumnId === "Uncategorized" && (stackByField.type === 'singleSelect' || stackByField.type === 'text')) {
          newStackValue = null; 
        }
        // For numeric stackByField, convert targetColumnId back to number if needed
        if (stackByField.type === 'number') {
            newStackValue = parseFloat(targetColumnId);
            if(isNaN(newStackValue)) newStackValue = null; // or handle error
        }

        updateRecordValue(parseInt(currentTableId), recordId, stackByField.id, newStackValue);
      }
      return newTasks;
    });
  };
  
  if (!stackByField) {
    return <div className="container error-message" style={{padding: '1rem'}}>Kanban configuration error: 'Stack By' Field ID ({viewConfig.stack_by_field_id}) is invalid or not found.</div>;
  }
  if (isLoadingFields || isLoadingRecords && initialRecords.length === 0) {
      return <div className="container">Loading Kanban data...</div>;
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCorners} onDragEnd={handleDragEnd}>
      <div style={{ display: 'flex', flexDirection: 'row', overflowX: 'auto', padding: '20px 5px', minHeight: '300px' }}>
        {orderedColumnIds.map(columnId => (
          <KanbanColumn
            key={columnId}
            columnId={columnId}
            title={columnId} // Use columnId (stack value) as title
            records={tasksByColumnId[columnId] || []}
            cardFields={viewConfig.card_fields || []}
            allFields={fields}
          />
        ))}
      </div>
    </DndContext>
  );
};

export default KanbanBoard;
