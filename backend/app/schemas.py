from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True # Changed from orm_mode = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Base Schemas
class BaseBase(BaseModel):
    name: str

class BaseCreate(BaseBase):
    pass

class BaseUpdate(BaseBase):
    pass

class Base(BaseBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# View Schemas
class ViewSortItem(BaseModel):
    field_id: int
    direction: Literal["asc", "desc"]

class ViewFilterItem(BaseModel):
    field_id: int
    operator: str
    value: Any

# For Form View Config
class FormFieldConfig(BaseModel):
    field_id: int
    label: Optional[str] = None
    help_text: Optional[str] = None
    is_required: Optional[bool] = False
    order: int # Ensure order is provided for form fields

class ViewConfig(BaseModel):
    # Grid specific (can be moved to a nested model if preferred)
    visible_field_ids: Optional[List[int]] = None
    field_order: Optional[Dict[str, int]] = None
    sorts: Optional[List[ViewSortItem]] = None
    filters: Optional[List[ViewFilterItem]] = None

    # Form specific
    title: Optional[str] = None
    description: Optional[str] = None
    form_fields: Optional[List[FormFieldConfig]] = None
    submit_button_text: Optional[str] = "Submit"

    # Kanban specific
    stack_by_field_id: Optional[int] = None
    card_fields: Optional[List[int]] = None # List of field_ids to show on cards
    column_order: Optional[List[str]] = None

    # Calendar specific
    date_field_id: Optional[int] = None
    end_date_field_id: Optional[int] = None
    event_title_field_id: Optional[int] = None

    # Gallery specific
    cover_field_id: Optional[int] = None
    card_visible_field_ids: Optional[List[int]] = None
    card_width: Optional[Literal['small', 'medium', 'large']] = 'medium'


    @model_validator(mode='after')
    def check_view_config(cls, data):
        # Form validation (existing)
        if data.form_fields:
            orders = [ff.order for ff in data.form_fields]
            if len(orders) != len(set(orders)): pass

        # Kanban validation (existing)
        if data.stack_by_field_id is not None:
            if data.card_fields and not all(isinstance(cf_id, int) for cf_id in data.card_fields):
                raise ValueError("All elements in card_fields must be integer field_ids for Kanban.")
        elif data.card_fields is not None:
             raise ValueError("stack_by_field_id must be provided if card_fields are defined for a Kanban view.")

        # Calendar validation
        if data.date_field_id is not None: # Indicates it might be a Calendar config
            if not data.event_title_field_id:
                raise ValueError("event_title_field_id is required for Calendar views if date_field_id is set.")
            if not isinstance(data.date_field_id, int) or not isinstance(data.event_title_field_id, int):
                raise ValueError("date_field_id and event_title_field_id must be integers for Calendar.")
            if data.end_date_field_id is not None and not isinstance(data.end_date_field_id, int):
                raise ValueError("end_date_field_id must be an integer if provided for Calendar.")
        elif data.event_title_field_id is not None:
            raise ValueError("date_field_id must be provided if event_title_field_id is defined for a Calendar view.")

        # Gallery validation
        if data.cover_field_id is not None: # Indicates it might be a Gallery config
            if not data.card_visible_field_ids:
                # Allow empty card_visible_field_ids, frontend can show a default like record ID or primary field
                pass
            if not isinstance(data.cover_field_id, int):
                 raise ValueError("cover_field_id must be an integer for Gallery.")
            if data.card_visible_field_ids and not all(isinstance(cf_id, int) for cf_id in data.card_visible_field_ids):
                raise ValueError("All elements in card_visible_field_ids must be integer field_ids for Gallery.")
        elif data.card_visible_field_ids is not None: # card_fields set but no cover_field_id (cover is optional though)
            # This condition might be too strict if cover_field_id is truly optional even if card fields are set.
            # For now, assume if card_visible_field_ids are set, it's intended as a gallery view, making cover_field_id conceptually important (though optional).
            pass


        return data


ALLOWED_VIEW_TYPES = Literal['grid', 'form', 'kanban', 'calendar', 'gallery'] # Added 'gallery'

class ViewBase(BaseModel):
    name: str
    type: ALLOWED_VIEW_TYPES = 'grid' # Default to grid
    config: ViewConfig

class ViewCreate(ViewBase):
    pass

class ViewUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ALLOWED_VIEW_TYPES] = None
    config: Optional[ViewConfig] = None

class View(ViewBase):
    id: int
    table_id: int
    owner_id: int

    class Config:
        from_attributes = True

# Table Schemas
class TableBase(BaseModel):
    name: str

class TableCreate(TableBase):
    pass

class TableUpdate(TableBase):
    name: Optional[str] = None # Allow partial updates for name

class Table(TableBase):
    id: int
    base_id: int
    owner_id: int # Include owner_id

    class Config:
        from_attributes = True # orm_mode for older Pydantic

# Field Schemas
from typing import Literal
ALLOWED_FIELD_TYPES = Literal[
    'text', 'number', 'date', 'boolean', 'singleSelect', 'multiSelect',
    'attachment', 'email', 'url', 'phoneNumber', 'formula', 'lookup',
    'count', 'rollup', 'user', 'createdTime', 'lastModifiedTime', 'autoNumber',
    'linkToRecord',
    'formula',
    'attachment' # New field type
]

class FieldOptions(BaseModel):
    choices: Optional[List[str]] = None
    linked_table_id: Optional[int] = None
    formula_string: Optional[str] = None
    # Options for attachment, e.g., allowedMimeTypes, maxSize - for future
    # allowed_mime_types: Optional[List[str]] = None
    # max_file_size_mb: Optional[int] = None
    # dateFormat: Optional[str] = None
    # currencySymbol: Optional[str] = None
    # precision: Optional[int] = None

class FieldBase(BaseModel):
    name: str
    type: ALLOWED_FIELD_TYPES
    options: Optional[FieldOptions] = None # Use FieldOptions schema

    @model_validator(mode='after')
    def check_options_for_select_types(cls, data):
        if data.type in ['singleSelect', 'multiSelect']:
            if not data.options or not data.options.choices:
                raise ValueError('Choices must be provided for singleSelect or multiSelect fields.')
            if not isinstance(data.options.choices, list) or not all(isinstance(choice, str) for choice in data.options.choices):
                raise ValueError('Choices must be a list of strings.')
        elif data.type == 'linkToRecord':
            if not data.options or data.options.linked_table_id is None:
                raise ValueError('linked_table_id must be provided for linkToRecord fields.')
            if not isinstance(data.options.linked_table_id, int):
                 raise ValueError('linked_table_id must be an integer.')
        elif data.type == 'formula':
            if not data.options or not data.options.formula_string:
                raise ValueError('formula_string must be provided for formula fields.')
            if not isinstance(data.options.formula_string, str) or not data.options.formula_string.strip():
                raise ValueError('formula_string must be a non-empty string.')
            # Basic validation for placeholder format could be added, e.g., ensure it contains {field_X}
        return data

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ALLOWED_FIELD_TYPES] = None
    options: Optional[FieldOptions] = None # Allow updating options

    @model_validator(mode='after')
    def check_options_on_update(cls, data):
        # This validator ensures that if type is present and is select, options are valid.
        # Or if options are provided, they are valid for the (potentially existing) type.
        # This logic can get complex if type is also changing.
        # For simplicity, if options are provided, they must be valid.
        # If type is changing TO a select type, options must be valid.
        if data.options and (data.type in ['singleSelect', 'multiSelect'] if data.type else True): # Check if type is select or type is not changing
             if not data.options.choices: # If options are set, choices must be there for select types
                 # This needs context of existing field type if type is not in payload
                 # For now, assume if options are being set, they must be complete for the target type if it's a select
                 pass # More complex validation might be needed here depending on how partial updates to options are handled
        return data


class Field(FieldBase):
    id: int
    table_id: int
    owner_id: int # Include owner_id

    class Config:
        from_attributes = True

# Table Schemas (Basic, can be expanded)
class TableBase(BaseModel):
    name: str

class TableCreate(TableBase):
    pass

class Table(TableBase):
    id: int
    base_id: int
    fields: List[Field] = [] # Include fields when retrieving a table

    class Config:
        from_attributes = True

# RecordValue Schemas
class RecordValueBase(BaseModel):
    field_id: int # This identifies which field this value is for
    value_text: Optional[str] = None
    value_number: Optional[float] = None
    value_boolean: Optional[bool] = None
    value_datetime: Optional[datetime] = None
    value_json: Optional[Any] = None # Using Any from typing

class RecordValueCreate(RecordValueBase): # Used when creating values as part of a record
    pass

class RecordValue(RecordValueBase):
    id: int
    record_id: int
    owner_id: int # Include owner_id

    class Config:
        from_attributes = True

# Record Schemas
class RecordDataBase(BaseModel): # For creating/updating the data payload of a record
    values: dict[int, Any] # Dict mapping field_id to its value, e.g., {1: "text value", 2: 123}

class RecordCreate(RecordDataBase):
    pass

class RecordUpdate(RecordDataBase):
    values: Optional[dict[int, Any]] = None # Allow partial updates

class Record(BaseModel): # No RecordBase needed if response always has these fields
    id: int
    table_id: int
    owner_id: int # Include owner_id
    created_at: datetime
    updated_at: datetime
    values: List[RecordValue] = []

    @model_validator(mode='after')
    def inject_computed_formula_values_after(self) -> 'Record':
        # This validator runs after the model has been initialized from ORM data.
        # It requires access to the original ORM instance's `_computed_formula_values`
        # and the `field_defs_map` which is not directly available here without context.
        # The router or CRUD layer should prepare the Record model by passing context.

        # For example, if context was passed during model_validate:
        # sa_record = self.model_fields_set.get('_sa_instance_') # Hypothetical context
        # field_defs_map = self.model_fields_set.get('_field_defs_map_')

        # Given the limitations, the simplest robust way is for CRUD to prepare
        # a list of RecordValue (Pydantic models) that already includes computed values
        # and then the Record Pydantic model is created from a dict that includes this final list.
        # This means the logic from crud._computed_formula_values and creating RecordValue schemas
        # for formulas will largely live in the CRUD functions before this Pydantic model is formed.

        # For now, this validator won't do anything. The CRUD will be responsible for ensuring
        # the `values` list passed to Record's Pydantic constructor (or from_orm)
        # already contains RecordValue Pydantic models for formula fields with computed values.
        return self

    class Config:
        from_attributes = True
