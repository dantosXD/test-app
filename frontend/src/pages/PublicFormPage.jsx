import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import formService from '../services/formService'; // Assuming you created this

const PublicFormPage = () => {
  const { viewId } = useParams();
  const [formConfig, setFormConfig] = useState(null);
  const [formData, setFormData] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    const fetchConfig = async () => {
      if (!viewId) return;
      setIsLoading(true);
      setError('');
      setSuccessMessage('');
      try {
        const config = await formService.getPublicFormConfig(viewId);
        setFormConfig(config);
        // Initialize formData state based on form_fields
        const initialData = {};
        if (config && config.form_fields) {
          config.form_fields.forEach(field => {
            initialData[String(field.id)] = ''; // Initialize with empty strings or default based on type
          });
        }
        setFormData(initialData);
      } catch (err) {
        setError(err.detail || err.message || 'Failed to load form configuration.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchConfig();
  }, [viewId]);

  const handleInputChange = (fieldId, value, fieldType) => {
    setFormData(prev => ({
      ...prev,
      [String(fieldId)]: fieldType === 'boolean' ? (event.target.checked) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');
    setIsLoading(true);

    // Basic client-side validation for required fields
    for (const ff of formConfig.form_fields) {
      if (ff.is_required && (formData[String(ff.id)] === undefined || String(formData[String(ff.id)]).trim() === '')) {
        setError(`Field "${ff.label}" is required.`);
        setIsLoading(false);
        return;
      }
    }

    // Prepare data for submission (ensure field IDs are strings if backend expects that for Dict keys)
    const submissionPayload = { ...formData };
    // Potentially convert types here if needed, e.g., for numbers, booleans
    // For now, backend's _map_value_to_record_value_columns handles some conversion
    formConfig.form_fields.forEach(field => {
        const key = String(field.id);
        if (field.type === 'number' && submissionPayload[key] !== '') {
            submissionPayload[key] = parseFloat(submissionPayload[key]);
            if (isNaN(submissionPayload[key])) submissionPayload[key] = null; // Or handle error
        } else if (field.type === 'boolean') {
            // Already boolean from checkbox's e.target.checked
        }
    });


    try {
      const result = await formService.submitPublicForm(viewId, submissionPayload);
      setSuccessMessage(result.message || 'Form submitted successfully!');
      // Clear form data after successful submission
      const initialData = {};
      formConfig.form_fields.forEach(field => {
        initialData[String(field.id)] = '';
      });
      setFormData(initialData);

    } catch (err) {
      setError(err.detail || err.message || 'Failed to submit form.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading && !formConfig) {
    return <div className="container" style={{textAlign: 'center', paddingTop: '50px'}}>Loading form...</div>;
  }

  if (error && !formConfig) { // Show error if config loading failed
    return <div className="container error-message" style={{textAlign: 'center', paddingTop: '50px'}}>Error: {error}</div>;
  }

  if (!formConfig) { // Should be covered by isLoading or error, but as a fallback
    return <div className="container" style={{textAlign: 'center', paddingTop: '50px'}}>Form not found or not available.</div>;
  }

  return (
    <div className="container" style={{ maxWidth: '700px', margin: '2rem auto', padding: '2rem', border: '1px solid #eee', borderRadius: '8px', backgroundColor: '#fff' }}>
      <h2 style={{textAlign: 'center'}}>{formConfig.title || formConfig.view_name}</h2>
      {formConfig.description && <p style={{textAlign: 'center', marginBottom: '2rem'}}>{formConfig.description}</p>}

      {successMessage && <div style={{padding: '1rem', marginBottom: '1rem', backgroundColor: 'lightgreen', color: 'darkgreen', border: '1px solid green', borderRadius: '4px'}}>{successMessage}</div>}
      {error && !successMessage && <div className="error-message" style={{padding: '1rem', marginBottom: '1rem'}}>{error}</div>}


      <form onSubmit={handleSubmit}>
        {formConfig.form_fields.map(field => (
          <div key={field.id} style={{ marginBottom: '1.5rem' }}>
            <label htmlFor={`form-field-${field.id}`} style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
              {field.label} {field.is_required && <span style={{ color: 'red' }}>*</span>}
            </label>
            {field.help_text && <small style={{ display: 'block', marginBottom: '0.5rem', color: '#555' }}>{field.help_text}</small>}

            {field.type === 'singleSelect' && field.options?.choices ? (
              <select
                id={`form-field-${field.id}`}
                value={formData[String(field.id)] || ''}
                onChange={(e) => handleInputChange(field.id, e.target.value, field.type)}
                required={field.is_required}
                style={{ padding: '0.75rem', width: '100%', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #ccc' }}
              >
                <option value="">-- Select {field.label} --</option>
                {field.options.choices.map(choice => <option key={choice} value={choice}>{choice}</option>)}
              </select>
            ) : field.type === 'boolean' ? (
              <input
                type="checkbox"
                id={`form-field-${field.id}`}
                checked={!!formData[String(field.id)]}
                onChange={(e) => handleInputChange(field.id, e.target.checked, field.type)}
                style={{ height: '1.2rem', width: '1.2rem', verticalAlign: 'middle' }}
              />
            ) : field.type === 'text' && (field.label.toLowerCase().includes('description') || field.help_text?.toLowerCase().includes('long text')) ? ( // Simple heuristic for textarea
                <textarea
                    id={`form-field-${field.id}`}
                    value={formData[String(field.id)] || ''}
                    onChange={(e) => handleInputChange(field.id, e.target.value, field.type)}
                    required={field.is_required}
                    rows={4}
                    style={{ padding: '0.75rem', width: '100%', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #ccc' }}
                />
            ) : (
              <input
                type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : field.type === 'email' ? 'email' : field.type === 'url' ? 'url' : 'text'}
                id={`form-field-${field.id}`}
                value={formData[String(field.id)] || ''}
                onChange={(e) => handleInputChange(field.id, e.target.value, field.type)}
                required={field.is_required}
                style={{ padding: '0.75rem', width: '100%', boxSizing: 'border-box', borderRadius: '4px', border: '1px solid #ccc' }}
              />
            )}
          </div>
        ))}
        <button type="submit" disabled={isLoading} style={{ padding: '0.75rem 2rem', width: '100%', fontSize: '1.1rem' }}>
          {isLoading ? 'Submitting...' : (formConfig.submit_button_text || 'Submit')}
        </button>
      </form>
    </div>
  );
};

export default PublicFormPage;
