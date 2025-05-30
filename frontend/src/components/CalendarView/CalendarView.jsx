import React, { useMemo } from 'react';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import listPlugin from '@fullcalendar/list';
import interactionPlugin from '@fullcalendar/interaction'; // for eventClick, dateClick, eventDrop, etc.
import useAppStore from '../../store/appStore'; // For fields and updateRecordValue

const CalendarViewComponent = ({ records, viewConfig }) => {
  const { fields, updateRecordValue, currentTableId } = useAppStore();

  const events = useMemo(() => {
    if (!records || !fields.length || !viewConfig || !viewConfig.date_field_id || !viewConfig.event_title_field_id) {
      return [];
    }

    const dateFieldId = viewConfig.date_field_id;
    const endDateFieldId = viewConfig.end_date_field_id;
    const titleFieldId = viewConfig.event_title_field_id;

    const dateField = fields.find(f => f.id === dateFieldId);
    const titleField = fields.find(f => f.id === titleFieldId);
    const endDateField = endDateFieldId ? fields.find(f => f.id === endDateFieldId) : null;

    if (!dateField || !titleField) {
      console.error("Calendar view config: Invalid date_field_id or event_title_field_id.");
      return [];
    }

    return records.map(record => {
      const recordValuesMap = record.values.reduce((acc, rv) => {
        acc[rv.field_id] = rv;
        return acc;
      }, {});

      const startDateValue = recordValuesMap[dateFieldId];
      const endDateValue = endDateFieldId ? recordValuesMap[endDateFieldId] : null;
      const titleValueContainer = recordValuesMap[titleFieldId];

      let title = `Record ${record.id}`; // Default title
      if (titleValueContainer) {
        title = titleValueContainer.value_text || titleValueContainer.value_number || titleValueContainer.value_json || title;
      }

      let start = null;
      if (startDateValue) {
        start = startDateValue.value_datetime || startDateValue.value_date || startDateValue.value_text; // Adapt based on how dates are stored
      }

      let end = null;
      if (endDateField && endDateValue) {
        end = endDateValue.value_datetime || endDateValue.value_date || endDateValue.value_text;
      }

      // Determine if allDay event
      // FullCalendar typically expects ISO strings or Date objects.
      // If only date (no time) is stored, it's an allDay event.
      // This logic might need refinement based on actual date storage format.
      const allDay = dateField.type === 'date' && (!endDateField || endDateField.type === 'date');


      if (!start) return null; // Cannot render event without start date

      return {
        id: String(record.id),
        title: String(title),
        start: new Date(start), // Ensure it's a Date object or valid ISO string
        end: end ? new Date(end) : null,
        allDay: allDay,
        // extendedProps: { recordData: record } // For eventClick to access full record
      };
    }).filter(event => event !== null);
  }, [records, fields, viewConfig]);

  const handleEventDrop = async (eventDropInfo) => {
    const { event } = eventDropInfo;
    const recordId = parseInt(event.id);
    const dateFieldId = viewConfig.date_field_id;
    const endDateFieldId = viewConfig.end_date_field_id;

    let newStartDate = event.startStr; // FullCalendar provides ISO string
    let newEndDate = event.endStr;   // Can be null if event is resized to be single day after being multi-day

    // If allDay, FullCalendar might only provide date part of ISO string.
    // Backend date field might expect full datetime or just date. Adjust if necessary.
    // For now, assume backend handles ISO string appropriately.

    // Update start date
    await updateRecordValue(parseInt(currentTableId), recordId, dateFieldId, newStartDate);

    // Update end date if it exists and changed
    if (endDateFieldId && event.end) { // event.end might be null if dragged to be a single day event
        await updateRecordValue(parseInt(currentTableId), recordId, endDateFieldId, newEndDate);
    } else if (endDateFieldId && !event.end && viewConfig.end_date_field_id) {
        // If event was made into a single day event from a multi-day one, clear the end date.
        await updateRecordValue(parseInt(currentTableId), recordId, endDateFieldId, null);
    }
    // Note: updateRecordValue in appStore constructs the full record payload.
    // This is inefficient but matches current design.
  };

  const handleEventClick = (clickInfo) => {
    // Basic alert, can be expanded to a modal showing record details
    alert(`Event Clicked: ${clickInfo.event.title}\nRecord ID: ${clickInfo.event.id}`);
    // console.log("Clicked event:", clickInfo.event.extendedProps.recordData);
  };


  if (!viewConfig || !viewConfig.date_field_id || !viewConfig.event_title_field_id) {
    return <div className="container error-message">Calendar view is not configured correctly. Please set Date Field and Event Title Field.</div>;
  }

  return (
    <div className="calendar-container" style={{marginTop: '20px', backgroundColor: 'white', padding: '15px', borderRadius: '5px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, listPlugin, interactionPlugin]}
        headerToolbar={{
          left: 'prev,next today',
          center: 'title',
          right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
        }}
        initialView="dayGridMonth"
        events={events}
        editable={true} // Allows dragging and resizing
        selectable={true} // Allows date clicking/selecting
        eventDrop={handleEventDrop}
        // eventResize={handleEventResize} // TODO: Implement if needed
        // dateClick={handleDateClick} // TODO: For creating new events by clicking on a date
        eventClick={handleEventClick}
        height="auto" // Adjusts height to content, or set specific like "650px"
        contentHeight="auto"
      />
    </div>
  );
};

export default CalendarViewComponent;
