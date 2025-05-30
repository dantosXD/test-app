import React from 'react';

// Helper to extract the actual value from a record value object based on field type
// This is similar to the one in KanbanCard, could be centralized if used often.
const getDisplayValueForCard = (field, recordValue) => {
    if (!recordValue) return 'N/A';

    switch (field.type) {
      case 'text': case 'email': case 'url': case 'phoneNumber': case 'singleSelect':
        return recordValue.value_text || '';
      case 'number':
        return recordValue.value_number !== null ? String(recordValue.value_number) : '';
      case 'boolean':
        return recordValue.value_boolean !== null ? String(recordValue.value_boolean) : '';
      case 'date': case 'createdTime': case 'lastModifiedTime':
        return recordValue.value_datetime ? new Date(recordValue.value_datetime).toLocaleDateString() : '';
      case 'multiSelect': case 'linkToRecord': // LinkToRecord stores array of IDs
        return Array.isArray(recordValue.value_json) ? recordValue.value_json.join(', ') : (recordValue.value_json || '');
      case 'attachment':
        return Array.isArray(recordValue.value_json) ? `${recordValue.value_json.length} file(s)` : '0 files';
      case 'formula':
        return recordValue.value_number !== null ? String(recordValue.value_number) : (recordValue.value_text || '');
      default:
        return 'Unsupported field type';
    }
  };


const GalleryCard = ({ record, viewConfig, allFields, onCardClick }) => {
  const { cover_field_id, card_visible_field_ids, card_width } = viewConfig;

  const cardStyle = {
    border: '1px solid #ddd',
    borderRadius: '8px',
    padding: '15px',
    marginBottom: '15px',
    backgroundColor: 'white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    cursor: onCardClick ? 'pointer' : 'default',
    width: card_width === 'small' ? '200px' : card_width === 'large' ? '400px' : '300px', // Example widths
    margin: '10px',
    display: 'flex',
    flexDirection: 'column'
  };

  const coverImageStyle = {
    width: '100%',
    height: card_width === 'small' ? '120px' : card_width === 'large' ? '240px' : '180px',
    objectFit: 'cover',
    borderRadius: '4px 4px 0 0',
    backgroundColor: '#f0f0f0', // Placeholder color
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#aaa',
    fontSize: '0.9em'
  };

  let coverImageUrl = null;
  let coverImageAlt = "Cover image placeholder";

  if (cover_field_id) {
    const coverFieldDefinition = allFields.find(f => f.id === cover_field_id);
    if (coverFieldDefinition && coverFieldDefinition.type === 'attachment') {
      const recordValue = record.values.find(rv => rv.field_id === cover_field_id);
      if (recordValue && Array.isArray(recordValue.value_json) && recordValue.value_json.length > 0) {
        const firstAttachment = recordValue.value_json[0];
        // Check if it's an image (basic check)
        if (firstAttachment.content_type && firstAttachment.content_type.startsWith('image/')) {
          // Assuming apiClient.defaults.baseURL is set or URLs are absolute
          // If URLs are relative like "/files/download/...", prepend backend URL
          const backendBaseUrl = "http://localhost:8000"; // Or from config
          coverImageUrl = firstAttachment.url.startsWith('http') ? firstAttachment.url : `${backendBaseUrl}${firstAttachment.url}`;
          coverImageAlt = firstAttachment.original_filename;
        } else {
            coverImageAlt = "First attachment is not an image";
        }
      } else {
         coverImageAlt = "No attachments in cover field";
      }
    } else {
        coverImageAlt = "Cover field is not an attachment type";
    }
  }

  return (
    <div style={cardStyle} onClick={() => onCardClick && onCardClick(record.id)}>
      {coverImageUrl ? (
        <img src={coverImageUrl} alt={coverImageAlt} style={coverImageStyle} />
      ) : (
        <div style={coverImageStyle}><span>{coverImageAlt}</span></div>
      )}
      <div style={{ padding: '10px 0 0 0' }}>
        {(card_visible_field_ids || []).map(fieldId => {
          const field = allFields.find(f => f.id === fieldId);
          const recordValue = record.values.find(rv => rv.field_id === fieldId);
          if (!field) return <div key={`field-${fieldId}-missing`} style={{fontSize: '0.8em', color: 'red'}}>Field ID {fieldId} not found</div>;

          return (
            <div key={field.id} style={{ marginBottom: '6px', fontSize: '0.9em' }}>
              <strong style={{ color: '#333', display: 'block' }}>{field.name}:</strong>
              <span style={{ color: '#666', wordBreak: 'break-word' }}>
                {getDisplayValueForCard(field, recordValue)}
              </span>
            </div>
          );
        })}
        {(!card_visible_field_ids || card_visible_field_ids.length === 0) && (
            <p style={{fontSize: '0.9em', color: '#555'}}>Record ID: {record.id}</p> // Fallback if no fields selected for card
        )}
      </div>
    </div>
  );
};

export default GalleryCard;
