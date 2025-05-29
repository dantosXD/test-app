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
    'count', 'rollup', 'user', 'createdTime', 'lastModifiedTime', 'autoNumber'
]

class FieldBase(BaseModel):
    name: str
    type: ALLOWED_FIELD_TYPES
    options: Optional[dict] = None

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel): # Changed to BaseModel for more flexibility if needed, or can be FieldBase
    name: Optional[str] = None
    type: Optional[ALLOWED_FIELD_TYPES] = None
    options: Optional[dict] = None


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
    values: List[RecordValue] = [] # List of RecordValue objects

    class Config:
        from_attributes = True
