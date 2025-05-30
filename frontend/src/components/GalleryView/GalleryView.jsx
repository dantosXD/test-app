import React from 'react';
import useAppStore from '../../store/appStore'; // To access allFields definition
import GalleryCard from './GalleryCard';

const GalleryViewComponent = ({ records, viewConfig }) => {
  const { fields: allFieldsFromStore } = useAppStore(); // Get all field definitions for context

  if (!viewConfig) {
    return <div className="container error-message">Gallery view configuration is missing.</div>;
  }

  const { title, card_visible_field_ids, cover_field_id, card_width } = viewConfig;

  // Ensure card_visible_field_ids is an array, even if undefined or null in config
  const visibleFieldIdsOnCard = Array.isArray(card_visible_field_ids) ? card_visible_field_ids : [];


  const galleryStyle = {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '20px', // Spacing between cards
    padding: '20px 0', // Padding around the gallery
    justifyContent: 'center', // Center cards if they don't fill the row
  };
  
  const handleCardClick = (recordId) => {
    // For now, basic alert. Later, can open a record detail modal or page.
    alert(`Card clicked for Record ID: ${recordId}`);
    // Example: navigate(`/records/${recordId}`) or openModal(recordId)
  };

  return (
    <div className="gallery-view-container">
      {title && <h3 style={{ textAlign: 'center', margin: '20px 0' }}>{title}</h3>}
      
      {(!records || records.length === 0) && <p style={{textAlign: 'center'}}>No records to display in this gallery.</p>}

      <div style={galleryStyle}>
        {records.map(record => {
            // We need to pass the full record.values to GalleryCard,
            // and let GalleryCard pick the values using its own logic with allFieldsFromStore.
            // The record object from appStore already has `values` as a list of RecordValue objects.
            // We need to transform it into a map {field_id: value_object} for easier lookup in GalleryCard,
            // or pass `allFieldsFromStore` and let GalleryCard iterate record.values.
            // The latter is simpler here.
            // The `record` objects passed to this component should be the ones from `appStore.records`
            // which are already processed by `TableDetailPage`'s `tableData` useMemo to have a
            // `values` property that is a map: { field_id: primitive_value }. Let's assume that structure.
            // If not, `GalleryCard` needs to be adjusted or data transformed here.
            // Based on current `TableDetailPage.tableData`, `record.values` is NOT a map, it's the raw list.
            // So, GalleryCard's `getDisplayValue` needs to work with `record.values` list and `allFieldsFromStore`.
            // The `GalleryCard` was written assuming `record.values` is already a map of {fieldId: primitiveValue}.
            // Let's adjust GalleryCard or transform data here.
            // For now, assuming GalleryCard can handle the raw `record.values` list if `allFields` is passed.
            // The `GalleryCard`'s `getDisplayValue` expects `recordValues` which should be `record.values` (the array from Pydantic)
            // and `allFields` to find field definitions.

            // Re-mapping record.values for GalleryCard if it expects a map {fieldId: primitiveValue}
            // This is what `TableDetailPage.tableData` does for React Table.
            // Let's ensure `GalleryCard` uses a similar approach or we do it here.
            // `GalleryCard`'s `getDisplayValue` takes `field` and `recordValue` (single rv object).
            // It should iterate through `record.values` to find the one for a given `fieldId`.
            // The current `GalleryCard` expects `record.values` to be a map of { field_id: primitive_value } which is what `TableDetailPage.tableData` creates.
            // So, the `records` prop for `GalleryViewComponent` should ideally be this `tableData`.
            // Let's assume `records` prop is already the transformed `tableData`.

          return (
            <GalleryCard
              key={record.id}
              record={record} // record here should have `values` as a map {field_id: primitive_value}
              viewConfig={{ // Pass only relevant parts of viewConfig to card
                cover_field_id, 
                card_visible_field_ids: visibleFieldIdsOnCard, 
                card_width 
              }}
              allFields={allFieldsFromStore} // Pass all field definitions
              onCardClick={handleCardClick}
            />
          );
        })}
      </div>
    </div>
  );
};

export default GalleryViewComponent;
