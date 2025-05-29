from sqlalchemy.orm import Session
from . import models, schemas, auth

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Base CRUD operations
def create_base(db: Session, base: schemas.BaseCreate, owner_id: int):
    db_base = models.Base(**base.model_dump(), owner_id=owner_id)
    db.add(db_base)
    db.commit()
    db.refresh(db_base)
    return db_base

def get_bases_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Base).filter(models.Base.owner_id == owner_id).offset(skip).limit(limit).all()

def get_base(db: Session, base_id: int, owner_id: int):
    return db.query(models.Base).filter(models.Base.id == base_id, models.Base.owner_id == owner_id).first()

def update_base(db: Session, base_id: int, base_update: schemas.BaseUpdate, owner_id: int):
    db_base = db.query(models.Base).filter(models.Base.id == base_id, models.Base.owner_id == owner_id).first()
    if db_base:
        update_data = base_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_base, key, value)
        db.commit()
        db.refresh(db_base)
    return db_base

def delete_base(db: Session, base_id: int, owner_id: int):
    db_base = db.query(models.Base).filter(models.Base.id == base_id, models.Base.owner_id == owner_id).first()
    if db_base:
        db.delete(db_base)
        db.commit()
    return db_base # Returns the object if found and deleted, else None if not found


# Table CRUD operations
def create_base_table(db: Session, table: schemas.TableCreate, base_id: int, user_id: int):
    # Verify base exists and is owned by the user
    db_base = db.query(models.Base).filter(models.Base.id == base_id, models.Base.owner_id == user_id).first()
    if not db_base:
        # Prefer 404 if base_id itself is not found, 403 if found but not owned.
        # For simplicity here, raising 404 if not found *or* not owned by this user for this base_id.
        # A more granular check might be:
        # db_base_exists = db.query(models.Base).filter(models.Base.id == base_id).first()
        # if not db_base_exists: raise HTTPException(status_code=404, detail="Base not found")
        # if db_base_exists.owner_id != user_id: raise HTTPException(status_code=403, detail="Not authorized to add table to this base")
        from fastapi import HTTPException # Local import to avoid circular dependency if crud is imported widely
        raise HTTPException(status_code=404, detail="Base not found or user does not have access to this base")

    db_table = models.Table(**table.model_dump(), base_id=base_id, owner_id=user_id)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

def get_tables_by_base(db: Session, base_id: int, user_id: int, skip: int = 0, limit: int = 100):
    # Verify base exists and is owned by the user
    db_base = db.query(models.Base).filter(models.Base.id == base_id, models.Base.owner_id == user_id).first()
    if not db_base:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Base not found or user does not have access to this base")
    
    return db.query(models.Table).filter(models.Table.base_id == base_id, models.Table.owner_id == user_id).offset(skip).limit(limit).all()

def get_table(db: Session, table_id: int, user_id: int):
    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Table not found or user does not have access")
    return db_table

def update_table(db: Session, table_id: int, table_update: schemas.TableUpdate, user_id: int):
    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Table not found or user does not have access")
    
    update_data = table_update.model_dump(exclude_unset=True) # Use exclude_unset for partial updates
    for key, value in update_data.items():
        setattr(db_table, key, value)
    
    db.commit()
    db.refresh(db_table)
    return db_table

def delete_table(db: Session, table_id: int, user_id: int):
    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Table not found or user does not have access")
    
    db.delete(db_table)
    db.commit()
    return db_table # Return the deleted object

# Field CRUD operations
def create_table_field(db: Session, field: schemas.FieldCreate, table_id: int, user_id: int):
    # Verify table exists and is owned by the user
    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Table not found or user does not have access to this table")

    db_field = models.Field(**field.model_dump(), table_id=table_id, owner_id=user_id)
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

def get_fields_by_table(db: Session, table_id: int, user_id: int, skip: int = 0, limit: int = 100):
    # Verify table exists and is owned by the user
    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Table not found or user does not have access to this table")
    
    return db.query(models.Field).filter(models.Field.table_id == table_id, models.Field.owner_id == user_id).offset(skip).limit(limit).all()

def get_field(db: Session, field_id: int, user_id: int):
    db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.owner_id == user_id).first()
    if not db_field:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Field not found or user does not have access")
    return db_field

def update_field(db: Session, field_id: int, field_update: schemas.FieldUpdate, user_id: int):
    db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.owner_id == user_id).first()
    if not db_field:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Field not found or user does not have access")
    
    update_data = field_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_field, key, value)
    
    db.commit()
    db.refresh(db_field)
    return db_field

def delete_field(db: Session, field_id: int, user_id: int):
    db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.owner_id == user_id).first()
    if not db_field:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Field not found or user does not have access")
    
    db.delete(db_field)
    db.commit()
    return db_field # Return the deleted object

# Helper function for RecordValue
def _map_value_to_record_value_columns(field_type: str, value: schemas.Any) -> dict:
    # Basic mapping based on field type. This might need to be more robust
    # depending on how field types are defined and how validation is handled.
    if field_type in ['text', 'email', 'url', 'singleSelect', 'multiSelect', 'phoneNumber', 'formula', 'lookup', 'user', 'autoNumber']: # Types that might store as text or JSON
        # For select types, value might be a string or list of strings/numbers. Store in JSON for flexibility for now.
        if isinstance(value, (list, dict)):
            return {'value_json': value}
        return {'value_text': str(value) if value is not None else None}
    elif field_type == 'number':
        return {'value_number': float(value) if value is not None else None}
    elif field_type == 'date' or field_type == 'createdTime' or field_type == 'lastModifiedTime':
        # Assuming datetime comes as ISO string or datetime object, store as datetime
        # Pydantic might have already converted to datetime object if schema specifies `datetime`
        return {'value_datetime': value}
    elif field_type == 'boolean' or field_type == 'count': # Count could also be number
        return {'value_boolean': bool(value) if value is not None else None}
    elif field_type == 'attachment': # Attachments usually stored as JSON (list of URLs or file info)
        return {'value_json': value}
    else: # Default or unknown, try to store as text or JSON
        if isinstance(value, (list, dict)):
            return {'value_json': value}
        return {'value_text': str(value) if value is not None else None}


# Record CRUD operations
def create_table_record(db: Session, record_data: schemas.RecordCreate, table_id: int, user_id: int):
    from fastapi import HTTPException # Local import
    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found or user does not have access")

    # Create the Record instance
    db_record = models.Record(table_id=table_id, owner_id=user_id)
    db.add(db_record)
    db.flush() # Flush to get db_record.id for RecordValues

    # Create RecordValue instances
    for field_id_str, value in record_data.values.items():
        field_id = int(field_id_str) # Pydantic keys for dicts are often strings
        db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.table_id == table_id).first()
        if not db_field:
            # Or raise error, or skip this field value
            # For now, skip if field definition not found in this table
            # This also implies field.owner_id would match user_id via table ownership
            continue 
        
        value_columns = _map_value_to_record_value_columns(db_field.type, value)
        db_record_value = models.RecordValue(
            record_id=db_record.id,
            field_id=field_id,
            owner_id=user_id, 
            **value_columns
        )
        db.add(db_record_value)
    
    db.commit()
    db.refresh(db_record) # Refresh to load the 'values' relationship
    return db_record


def get_records_by_table(db: Session, table_id: int, user_id: int, skip: int = 0, limit: int = 100):
    from fastapi import HTTPException # Local import
    from sqlalchemy.orm import joinedload

    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table:
        raise HTTPException(status_code=404, detail="Table not found or user does not have access")
    
    records = db.query(models.Record).filter(models.Record.table_id == table_id, models.Record.owner_id == user_id)\
        .options(joinedload(models.Record.values).joinedload(models.RecordValue.field))\
        .offset(skip).limit(limit).all()
    return records

def get_record(db: Session, record_id: int, user_id: int):
    from fastapi import HTTPException # Local import
    from sqlalchemy.orm import joinedload

    db_record = db.query(models.Record).filter(models.Record.id == record_id, models.Record.owner_id == user_id)\
        .options(joinedload(models.Record.values).joinedload(models.RecordValue.field))\
        .first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found or user does not have access")
    return db_record

def update_record(db: Session, record_id: int, record_data: schemas.RecordUpdate, user_id: int):
    from fastapi import HTTPException # Local import
    from sqlalchemy.sql import func # For updated_at

    db_record = get_record(db, record_id, user_id) # Reuse get_record for initial fetch and auth check
    if not db_record: # Should be handled by get_record, but as a safeguard
        raise HTTPException(status_code=404, detail="Record not found or user does not have access")

    if record_data.values is not None:
        # Simple approach: Delete existing values and create new ones
        # More complex: diff and update/insert/delete selectively
        db.query(models.RecordValue).filter(models.RecordValue.record_id == record_id).delete()
        # Need to commit the delete if not auto-committed by session, or handle cascade if configured
        # db.flush() # Ensure deletes are processed before inserts if PK conflicts could occur (not here)

        for field_id_str, value in record_data.values.items():
            field_id = int(field_id_str)
            db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.table_id == db_record.table_id).first()
            if not db_field:
                # Skip or raise error for invalid field_id in update payload
                continue
            
            value_columns = _map_value_to_record_value_columns(db_field.type, value)
            db_record_value = models.RecordValue(
                record_id=db_record.id,
                field_id=field_id,
                owner_id=user_id,
                **value_columns
            )
            db.add(db_record_value)
            
    db_record.updated_at = func.now() # Manually update timestamp as SQLAlchemy onupdate might not trigger for relationship changes
    db.commit()
    db.refresh(db_record)
    # Re-fetch with joinedload to ensure the 'values' are fresh if they were modified.
    # Or, be careful about how 'values' are managed in the session after deletes/adds.
    # For simplicity, let's re-fetch using get_record which handles joined loading.
    return get_record(db, record_id, user_id)


def delete_record(db: Session, record_id: int, user_id: int):
    from fastapi import HTTPException # Local import
    db_record = db.query(models.Record).filter(models.Record.id == record_id, models.Record.owner_id == user_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found or user does not have access")
    
    # Deletion of RecordValues will be handled by cascade="all, delete-orphan" on Record.values relationship
    db.delete(db_record)
    db.commit()
    return db_record # Return the deleted object
