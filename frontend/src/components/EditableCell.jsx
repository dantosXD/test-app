import React, { useState, useEffect } from 'react';

// Simple EditableCell component
// For now, assumes text input. Can be expanded for different field types.
const EditableCell = ({ getValue, row, column, table }) => {
  const initialValue = getValue();
  const [value, setValue] = useState(initialValue);

  const fieldType = column.columnDef.meta?.type;
  const fieldOptions = column.columnDef.meta?.options;
  const readOnly = column.columnDef.meta?.readOnly;

  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  // When the input is blurred, we'll call the table meta's updateData function
  const onBlur = () => {
    if (!readOnly) { // Only update if not read-only
      table.options.meta?.updateData(row.original.id, column.id, value);
    }
  };

  if (readOnly) {
    return <div style={{ padding: '5px', whiteSpace: 'pre-wrap', width: '100%', boxSizing: 'border-box'  }}>{initialValue === null || initialValue === undefined ? '' : String(initialValue)}</div>;
  }

  if (fieldType === 'singleSelect') {
    return (
      <select
        value={value || ''}
        onChange={e => setValue(e.target.value)}
        onBlur={onBlur}
        style={{ width: '100%', border: 'none', padding: '5px', boxSizing: 'border-box', backgroundColor: 'transparent' }}
      >
        {(fieldOptions?.choices || []).map(choice => (
          <option key={choice} value={choice}>
            {choice}
          </option>
        ))}
        {!value && <option value="" disabled hidden></option>}
      </select>
    );
  } else if (fieldType === 'multiSelect') {
    // For multiSelect, editing as comma-separated string for now.
    // Displaying as string too. A proper display would iterate and show tags/pills.
    return (
      <input
        type="text"
        value={value === null || value === undefined ? '' : (Array.isArray(value) ? value.join(', ') : value) } // Display array as comma-sep string
        onChange={e => setValue(e.target.value)} // Will be string, needs parsing on update
        onBlur={onBlur} // The onBlur in table meta needs to parse this string back to array
        placeholder="Comma-separated values"
        style={{ width: '100%', border: 'none', padding: '5px', boxSizing: 'border-box' }}
      />
    );
  } else if (fieldType === 'linkToRecord') {
    // Display: Show count or comma-separated IDs. For now, comma-separated IDs.
    // Edit: Text input for comma-separated IDs. Modal is for later.
    const displayValue = Array.isArray(value) ? value.join(', ') : '';
    return (
      <input
        type="text"
        value={displayValue}
        onChange={e => setValue(e.target.value)} // Will be string, needs parsing on update
        onBlur={onBlur} // The onBlur in table meta needs to parse this string back to array of numbers
        placeholder="Comma-sep record IDs (e.g. 1,2)"
        title={Array.isArray(value) ? `Linked IDs: ${value.join(', ')}` : "No linked records"}
        style={{ width: '100%', border: 'none', padding: '5px', boxSizing: 'border-box' }}
      />
    );
  } else if (fieldType === 'attachment') {
    const attachments = Array.isArray(value) ? value : []; // value should be list of file metadata objects

    const handleFileChange = async (event) => {
        const files = event.target.files;
        if (!files || files.length === 0) return;

        // For simplicity, directly use fileService from here.
        // Ideally, this logic might be in a more structured place or passed via table meta.
        // This is a temporary import for brevity of example.
        const fileService = (await import('../services/fileService')).default;

        const uploadedFileMetadata = [];
        for (let i = 0; i < files.length; i++) {
            try {
                // TODO: Add progress indicator
                const metadata = await fileService.uploadFile(files[i]);
                uploadedFileMetadata.push(metadata);
            } catch (uploadError) {
                console.error("Failed to upload file:", files[i].name, uploadError);
                // Optionally show an error to the user for specific file
            }
        }

        // New value is existing attachments plus newly uploaded ones
        const newValue = [...attachments, ...uploadedFileMetadata];
        table.options.meta?.updateData(row.original.id, column.id, newValue);
    };

    const handleRemoveAttachment = (fileNameToRemove) => {
        const newValue = attachments.filter(att => att.filename !== fileNameToRemove);
        table.options.meta?.updateData(row.original.id, column.id, newValue);
    };

    return (
        <div style={{ padding: '5px' }}>
            {attachments.map((att, index) => (
                <div key={att.filename || index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2px', fontSize: '0.9em' }}>
                    <a href={table.options.meta?.apiBaseUrl ? `${table.options.meta.apiBaseUrl}${att.url}` : att.url} target="_blank" rel="noopener noreferrer" title={`Download ${att.original_filename}`}>
                        {att.original_filename} ({Math.round((att.size || 0) / 1024)}KB)
                    </a>
                    {!readOnly && (
                         <button onClick={() => handleRemoveAttachment(att.filename)} style={{padding:'2px 5px', fontSize:'0.8em', marginLeft:'5px', backgroundColor:'transparent', border:'1px solid #ccc', cursor:'pointer'}}>X</button>
                    )}
                </div>
            ))}
            {!readOnly && (
                <div style={{marginTop: attachments.length > 0 ? '5px' : '0'}}>
                    <input
                        type="file"
                        multiple
                        onChange={handleFileChange}
                        id={`file-upload-${row.original.id}-${column.id}`}
                        style={{display: 'none'}}
                    />
                    <label
                        htmlFor={`file-upload-${row.original.id}-${column.id}`}
                        style={{padding:'3px 6px', fontSize:'0.8em', backgroundColor:'#eee', border:'1px solid #ccc', borderRadius:'3px', cursor:'pointer'}}
                    >
                        + Add
                    </label>
                </div>
            )}
        </div>
    );
  }
  // Basic text input for other types (text, number, boolean, date for now)
  // Number, boolean, date might need more specific input types later
  let inputType = "text";
  if (fieldType === "number") inputType = "number";
  if (fieldType === "date") inputType = "date"; // Note: native date input stores as YYYY-MM-DD
  if (fieldType === "boolean") inputType = "checkbox";


  if (fieldType === "boolean") {
    return (
        <input
            type="checkbox"
            checked={Boolean(value)}
            onChange={e => setValue(e.target.checked)}
            onBlur={onBlur} // onBlur might be better for checkbox if click doesn't fire update immediately
            style={{ margin: 'auto', display: 'block' }}
        />
    );
  }

  return (
    <input
      type={inputType}
      value={value === null || value === undefined ? '' : value}
      onChange={e => setValue(e.target.value)}
      onBlur={onBlur}
      style={{ width: '100%', border: 'none', padding: '5px', boxSizing: 'border-box' }}
    />
  );
};

export default EditableCell;
