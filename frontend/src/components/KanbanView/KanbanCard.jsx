import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const KanbanCard = ({ record, cardFields, allFields }) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: record.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    padding: '10px',
    margin: '0 0 8px 0',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '4px',
    boxShadow: isDragging ? '0 4px 8px rgba(0,0,0,0.1)' : '0 1px 2px rgba(0,0,0,0.05)',
    cursor: 'grab',
  };

  // Helper to get display value from record.values (which is keyed by field_id)
  const getDisplayValue = (fieldId, recordValues) => {
    const fieldDefinition = allFields.find(f => f.id === fieldId);
    const valueFromRecord = recordValues ? recordValues[fieldId] : undefined; // record.values is now { fieldId: value }

    if (valueFromRecord === undefined || valueFromRecord === null) return 'N/A';

    if (fieldDefinition) {
        switch (fieldDefinition.type) {
            case 'boolean': return String(valueFromRecord);
            case 'linkToRecord': return Array.isArray(valueFromRecord) ? `Links: ${valueFromRecord.join(', ')}` : 'N/A';
            case 'multiSelect': return Array.isArray(valueFromRecord) ? valueFromRecord.join(', ') : String(valueFromRecord);
            // Add more type-specific formatting if needed
            default: return String(valueFromRecord);
        }
    }
    return String(valueFromRecord);
  };


  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      {cardFields && cardFields.length > 0 ? (
        cardFields.map(fieldId => {
          const field = allFields.find(f => f.id === fieldId);
          return (
            <div key={fieldId} style={{ marginBottom: '5px', fontSize: '0.9em' }}>
              <strong style={{ color: '#555' }}>{field ? field.name : `Field ${fieldId}`}: </strong>
              {getDisplayValue(fieldId, record.values)}
            </div>
          );
        })
      ) : (
        // Fallback if no card_fields are configured, show record ID or primary field
        <div style={{ fontWeight: 'bold' }}>Record ID: {record.id}</div>
      )}
    </div>
  );
};

export default KanbanCard;
