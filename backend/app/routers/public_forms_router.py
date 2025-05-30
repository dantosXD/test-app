from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db # For DB session
# Assuming ConnectionManager is not directly needed here unless forms trigger real-time events to other systems
# from ..websocket_manager import get_connection_manager

router = APIRouter(
    prefix="/public/forms",
    tags=["public_forms"],
)

class PublicFormFieldDetail(schemas.FieldBase): # Extends FieldBase to include original field info
    id: int # Actual field ID
    label: str # Custom label from FormFieldConfig, or original field name
    help_text: Optional[str] = None
    is_required: bool = False
    # Type and options are inherited from FieldBase (which uses FieldOptions)
    # We need to ensure FieldBase.options uses the same FieldOptions model.
    # Current FieldBase.options is FieldOptions, which is good.

class PublicFormConfigResponse(BaseModel):
    view_id: int
    view_name: str
    table_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    submit_button_text: Optional[str] = "Submit"
    form_fields: List[PublicFormFieldDetail] = []


@router.get("/{view_id}", response_model=PublicFormConfigResponse)
async def get_public_form_config(view_id: int, db: Session = Depends(get_db)):
    # Fetch the view without user_id check for public access
    db_view = db.query(models.View).filter(models.View.id == view_id).first()

    if not db_view or db_view.type != 'form':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form view not found")

    if not db_view.config or not db_view.config.get('form_fields'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Form configuration is incomplete")

    form_config = schemas.ViewConfig.model_validate(db_view.config) # Parse raw JSON from DB

    response_form_fields: List[PublicFormFieldDetail] = []

    # Get all field IDs from the form config to fetch their definitions in one query
    configured_field_ids = [ff_conf.field_id for ff_conf in form_config.form_fields or []]
    if not configured_field_ids:
         # No fields configured for the form, or form_fields is empty
        pass # Return empty list of fields if none are configured

    db_fields = db.query(models.Field).filter(
        models.Field.id.in_(configured_field_ids),
        models.Field.table_id == db_view.table_id # Ensure fields belong to the view's table
    ).all()

    db_fields_map = {field.id: field for field in db_fields}

    for ff_config in sorted(form_config.form_fields or [], key=lambda f: f.order):
        field_model = db_fields_map.get(ff_config.field_id)
        if not field_model:
            # Configured field_id does not exist or doesn't belong to this table. Skip or error.
            # For now, we skip. Consider logging this inconsistency.
            continue

        response_form_fields.append(PublicFormFieldDetail(
            id=field_model.id,
            name=field_model.name, # Original field name
            label=ff_config.label or field_model.name, # Use custom label or default to field name
            help_text=ff_config.help_text,
            is_required=ff_config.is_required or False,
            type=field_model.type, # Original field type
            options=field_model.options # Original field options (e.g., choices for select)
        ))

    return PublicFormConfigResponse(
        view_id=db_view.id,
        view_name=db_view.name,
        table_id=db_view.table_id,
        title=form_config.title or db_view.name, # Default title to view name
        description=form_config.description,
        submit_button_text=form_config.submit_button_text or "Submit",
        form_fields=response_form_fields
    )


@router.post("/{view_id}")
async def submit_public_form(
    view_id: int,
    submission_data: Dict[str, Any], # e.g. {"field_123_id": "value", "field_456_id": "another value"}
    db: Session = Depends(get_db)
):
    db_view = db.query(models.View).filter(models.View.id == view_id).first()

    if not db_view or db_view.type != 'form':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form view not found")

    if not db_view.config or not db_view.config.get('form_fields'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Form configuration is incomplete")

    form_config = schemas.ViewConfig.model_validate(db_view.config)

    # Validate submission against form_fields config (is_required, types later if needed)
    record_values_payload: Dict[int, Any] = {} # To build {field_id: value} for crud.create_table_record

    configured_field_ids = {ff_conf.field_id: ff_conf for ff_conf in form_config.form_fields or []}
    db_fields_map = {
        field.id: field for field in
        db.query(models.Field).filter(models.Field.id.in_(configured_field_ids.keys())).all()
    }

    for ff_conf in form_config.form_fields or []:
        field_id = ff_conf.field_id
        field_model = db_fields_map.get(field_id)

        if not field_model: # Should not happen if config is validated on save
            continue

        submitted_value = submission_data.get(str(field_id)) # Form data keys might be strings

        if ff_conf.is_required and (submitted_value is None or str(submitted_value).strip() == ""):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Field '{ff_conf.label or field_model.name}' is required."
            )

        # Basic type conversion/validation before passing to CRUD could be done here
        # For now, crud._map_value_to_record_value_columns will handle basic conversions
        # The RecordCreate schema doesn't do per-field validation based on field type from DB
        record_values_payload[field_id] = submitted_value

    # Ensure owner_id for the new record is the owner_id of the View object
    record_owner_id = db_view.owner_id

    # The crud.create_table_record expects schemas.RecordCreate which has `values: dict[int, Any]`
    record_create_schema = schemas.RecordCreate(values=record_values_payload)

    try:
        # Note: create_table_record is async, ensure this endpoint is also async
        # The user_id for create_table_record here is the view's owner, who owns the table contextually for this form.
        new_record = await crud.create_table_record(
            db=db,
            record_data=record_create_schema,
            table_id=db_view.table_id,
            user_id=record_owner_id
        )
    except ValueError as ve: # Catch specific errors like from _map_value_to_record_value_columns
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(ve))
    except Exception as e:
        # Log actual error e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save submission.")

    return {"message": "Form submitted successfully", "record_id": new_record.id}
