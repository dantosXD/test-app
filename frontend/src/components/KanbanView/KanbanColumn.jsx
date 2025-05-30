import React from 'react';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import KanbanCard from './KanbanCard';

const KanbanColumn = ({ columnId, title, records, cardFields, allFields }) => {
  const columnStyle = {
    minHeight: '200px', // Ensure droppable area is available even if empty
    maxHeight: 'calc(100vh - 250px)', // Example max height
    overflowY: 'auto',
    padding: '10px',
    margin: '0 8px',
    backgroundColor: '#f4f4f4',
    borderRadius: '4px',
    width: '280px',
    flexShrink: 0, // Prevent columns from shrinking too much
  };

  const titleStyle = {
    padding: '8px',
    marginBottom: '10px',
    fontWeight: 'bold',
    textAlign: 'center',
    backgroundColor: '#e9e9e9',
    borderRadius: '3px',
  };

  return (
    <div style={columnStyle}>
      <div style={titleStyle}>{title} ({records.length})</div>
      <SortableContext items={records.map(r => r.id)} strategy={verticalListSortingStrategy}>
        {records.map(record => (
          <KanbanCard 
            key={record.id} 
            record={record} 
            cardFields={cardFields} 
            allFields={allFields} 
          />
        ))}
      </SortableContext>
    </div>
  );
};

export default KanbanColumn;
