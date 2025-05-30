from typing import Optional, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc, desc, String, cast
import re
from fastapi import HTTPException, status

from . import models, schemas, auth # auth for password hashing
from .permission_levels import PermissionLevel
from .websocket_manager import get_connection_manager
from app.formula_engine import evaluate_formula


# User CRUD
def get_user(db: Session, user_id: int): # ... (as before)
    return db.query(models.User).filter(models.User.id == user_id).first()
def get_user_by_email(db: Session, email: str): # ... (as before)
    return db.query(models.User).filter(models.User.email == email).first()
def create_user(db: Session, user: schemas.UserCreate): # ... (as before)
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, password_hash=hashed_password)
    db.add(db_user); db.commit(); db.refresh(db_user)
    return db_user

# Base CRUD 
def create_base(db: Session, base: schemas.BaseCreate, owner_id: int): # ... (as before)
    db_base = models.Base(**base.model_dump(), owner_id=owner_id)
    db.add(db_base); db.commit(); db.refresh(db_base)
    return db_base
def get_bases_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100): # ... (as before)
    return db.query(models.Base).filter(models.Base.owner_id == owner_id).offset(skip).limit(limit).all()
def get_base(db: Session, base_id: int, owner_id: int): # ... (as before)
    return db.query(models.Base).filter(models.Base.id == base_id, models.Base.owner_id == owner_id).first()
def update_base(db: Session, base_id: int, base_update: schemas.BaseUpdate, owner_id: int): # ... (as before)
    db_base = get_base(db, base_id=base_id, owner_id=owner_id)
    if not db_base: raise HTTPException(status_code=404, detail="Base not found or user does not have access")
    update_data = base_update.model_dump(exclude_unset=True)
    for key, value in update_data.items(): setattr(db_base, key, value)
    db.commit(); db.refresh(db_base)
    return db_base
def delete_base(db: Session, base_id: int, owner_id: int): # ... (as before)
    db_base = get_base(db, base_id=base_id, owner_id=owner_id)
    if not db_base: raise HTTPException(status_code=404, detail="Base not found or user does not have access")
    db.delete(db_base); db.commit()
    return db_base

# Table CRUD
def create_base_table(db: Session, table: schemas.TableCreate, base_id: int, user_id: int): # ... (as before)
    db_base = get_base(db, base_id=base_id, owner_id=user_id)
    if not db_base: raise HTTPException(status_code=404, detail="Base not found or user does not have access")
    db_table = models.Table(**table.model_dump(), base_id=base_id, owner_id=user_id)
    db.add(db_table); db.commit(); db.refresh(db_table)
    return db_table
def get_tables_by_base(db: Session, base_id: int, user_id: int, skip: int = 0, limit: int = 100): # ... (as before)
    db_base = get_base(db, base_id=base_id, owner_id=user_id)
    if not db_base: raise HTTPException(status_code=404, detail="Base not found or user does not have access")
    return db.query(models.Table).filter(models.Table.base_id == base_id, models.Table.owner_id == user_id).offset(skip).limit(limit).all()
def get_table(db: Session, table_id: int, user_id: int): # ... (as before)
    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table: raise HTTPException(status_code=404, detail="Table not found or user does not have access")
    return db_table
def update_table(db: Session, table_id: int, table_update: schemas.TableUpdate, user_id: int): # ... (as before)
    db_table = get_table(db, table_id=table_id, user_id=user_id)
    if not db_table: raise HTTPException(status_code=404, detail="Table not found or user does not have access")
    update_data = table_update.model_dump(exclude_unset=True)
    for key, value in update_data.items(): setattr(db_table, key, value)
    db.commit(); db.refresh(db_table)
    return db_table
def delete_table(db: Session, table_id: int, user_id: int): # ... (as before)
    db_table = get_table(db, table_id=table_id, user_id=user_id)
    if not db_table: raise HTTPException(status_code=404, detail="Table not found or user does not have access")
    db.delete(db_table); db.commit()
    return db_table

# Field CRUD
def create_table_field(db: Session, field: schemas.FieldCreate, table_id: int, user_id: int): # ... (as before)
    db_table = get_table(db, table_id=table_id, user_id=user_id)
    if not db_table: raise HTTPException(status_code=404, detail="Table not found or user does not have access")
    # Validate linked_table_id if type is linkToRecord
    if field.type == 'linkToRecord':
        if not field.options or field.options.linked_table_id is None:
            raise HTTPException(status_code=400, detail="linked_table_id is required in options for linkToRecord fields.")
        # Check if linked_table exists and user has access (e.g., same base or shared)
        # For now, just check existence. More complex access rules can be added.
        linked_table = db.query(models.Table).filter(models.Table.id == field.options.linked_table_id).first()
        if not linked_table:
            raise HTTPException(status_code=400, detail=f"Linked table with id {field.options.linked_table_id} not found.")
    db_field = models.Field(**field.model_dump(), table_id=table_id, owner_id=user_id)
    db.add(db_field); db.commit(); db.refresh(db_field)
    return db_field
def get_fields_by_table(db: Session, table_id: int, user_id: int, skip: int = 0, limit: int = 100): # ... (as before)
    # No direct ownership check on table for listing fields if user has table permission (handled by router/dependency)
    return db.query(models.Field).filter(models.Field.table_id == table_id).offset(skip).limit(limit).all()
def get_field(db: Session, field_id: int, user_id: int): # ... (as before) - this checks field ownership
    db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.owner_id == user_id).first()
    if not db_field: raise HTTPException(status_code=404, detail="Field not found or user does not have access")
    return db_field
def update_field(db: Session, field_id: int, field_update: schemas.FieldUpdate, user_id: int): # ... (as before)
    db_field = get_field(db, field_id=field_id, user_id=user_id) # Checks field ownership
    if not db_field: raise HTTPException(status_code=404, detail="Field not found or user does not have access")
    update_data = field_update.model_dump(exclude_unset=True)
    # Similar validation for linked_table_id if type is changing to/from linkToRecord or options are updated
    if 'options' in update_data and field_update.type == 'linkToRecord' :
        if not field_update.options or field_update.options.linked_table_id is None:
            raise HTTPException(status_code=400, detail="linked_table_id is required in options for linkToRecord fields.")
        linked_table = db.query(models.Table).filter(models.Table.id == field_update.options.linked_table_id).first()
        if not linked_table:
            raise HTTPException(status_code=400, detail=f"Linked table with id {field_update.options.linked_table_id} not found.")
    for key, value in update_data.items(): setattr(db_field, key, value)
    db.commit(); db.refresh(db_field)
    return db_field
def delete_field(db: Session, field_id: int, user_id: int): # ... (as before)
    db_field = get_field(db, field_id=field_id, user_id=user_id) # Checks field ownership
    if not db_field: raise HTTPException(status_code=404, detail="Field not found or user does not have access")
    db.delete(db_field); db.commit()
    return db_field

# RecordValue Helper
def _map_value_to_record_value_columns(field_type: str, value: Any) -> dict: # ... (as before)
    # ... (content from previous correct version including linkToRecord and attachment)
    if field_type == 'singleSelect':
        if value is not None and not isinstance(value, str): return {'value_text': str(value)}
        return {'value_text': value}
    elif field_type == 'multiSelect':
        if value is not None and not isinstance(value, list): raise ValueError("multiSelect value must be a list")
        if value is not None and any(not isinstance(item, str) for item in value): raise ValueError("All items in multiSelect value must be strings")
        return {'value_json': value}
    elif field_type == 'linkToRecord': # Expects list of int IDs
        if value is not None and not isinstance(value, list): raise ValueError("linkToRecord value must be a list of IDs")
        if value is not None and any(not isinstance(item, int) for item in value): raise ValueError("All items in linkToRecord value must be integer IDs")
        return {'value_json': value}
    elif field_type == 'attachment': # Expects list of file metadata objects
        if value is not None and not isinstance(value, list): raise ValueError("attachment value must be a list of file metadata objects")
        return {'value_json': value}
    elif field_type in ['text', 'email', 'url', 'phoneNumber', 'formula', 'lookup', 'user', 'autoNumber']:
        if isinstance(value, (list, dict)): return {'value_json': value}
        return {'value_text': str(value) if value is not None else None}
    elif field_type == 'number' or field_type == 'count':
        try: return {'value_number': float(value) if value is not None else None}
        except (ValueError, TypeError): raise ValueError(f"Invalid value for number field: {value}")
    elif field_type == 'date' or field_type == 'createdTime' or field_type == 'lastModifiedTime':
        return {'value_datetime': value}
    elif field_type == 'boolean':
        if isinstance(value, str): return {'value_boolean': value.lower() == 'true'}
        return {'value_boolean': bool(value) if value is not None else None}
    else: 
        if isinstance(value, (list, dict)): return {'value_json': value}
        return {'value_text': str(value) if value is not None else None}

# Record CRUD (permission checks updated)
async def create_table_record(db: Session, record_data: schemas.RecordCreate, table_id: int, user_id: int): # ... (as before with permission checks)
    manager = get_connection_manager()
    permission = get_user_table_permission_level(db, table_id=table_id, user_id=user_id)
    if not permission or permission not in [PermissionLevel.ADMIN, PermissionLevel.EDITOR]:
        raise HTTPException(status_code=403, detail="Not enough permissions to create records")
    db_record = models.Record(table_id=table_id, owner_id=user_id)
    db.add(db_record); db.flush()
    for field_id_str, value in record_data.values.items():
        field_id = int(field_id_str)
        db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.table_id == table_id).first()
        if not db_field or db_field.type == 'formula': continue
        value_columns = _map_value_to_record_value_columns(db_field.type, value)
        db.add(models.RecordValue(record_id=db_record.id, field_id=field_id, owner_id=user_id, **value_columns))
    db.commit(); db.refresh(db_record)
    if record_data.values:
        for field_id_str, value in record_data.values.items():
            field_id = int(field_id_str)
            db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.table_id == table_id).first()
            if db_field and db_field.type == 'linkToRecord' and isinstance(value, list):
                for linked_record_id in value:
                    db.add(models.RecordLink(source_record_id=db_record.id, source_field_id=field_id, linked_record_id=int(linked_record_id), owner_id=user_id))
        db.commit(); db.refresh(db_record)
    record_dto = get_record(db, db_record.id, user_id)
    await manager.broadcast_json_to_room({"event": "record_created", "data": record_dto.model_dump(exclude_none=True)}, f"table_{table_id}")
    return record_dto

def get_records_by_table(db: Session, table_id: int, user_id: int, skip: int = 0, limit: int = 100, sort_by_field_id: Optional[int] = None, sort_direction: Optional[str] = "asc", filter_by_field_id: Optional[int] = None, filter_value: Optional[str] = None): # ... (as before with permission checks)
    permission = get_user_table_permission_level(db, table_id=table_id, user_id=user_id)
    if not permission: raise HTTPException(status_code=403, detail="Not enough permissions")
    # ... (rest of the function including formula computation and returning list of Pydantic models)
    table_fields = db.query(models.Field).filter(models.Field.table_id == table_id).all()
    field_defs_map = {field.id: field for field in table_fields}
    formula_fields = [field for field in table_fields if field.type == 'formula']
    query = db.query(models.Record).filter(models.Record.table_id == table_id)
    if permission != PermissionLevel.ADMIN and permission != PermissionLevel.EDITOR : # If viewer, only own records? (This depends on desired logic)
        # This example assumes viewers can see all records in a table they have viewer access to.
        # If viewers should only see their own records (unless they are admin/editor), add:
        # query = query.filter(models.Record.owner_id == user_id)
        pass
    # ... (Filtering and Sorting logic as before) ...
    fetched_records_sa = query.options(joinedload(models.Record.values).joinedload(models.RecordValue.field)).offset(skip).limit(limit).all()
    processed_records_dto = []
    for record_sa in fetched_records_sa:
        current_record_values_map = {rv.field_id: rv for rv in record_sa.values}
        computed_formula_values = {}
        for formula_field in formula_fields:
            if formula_field.options and formula_field.options.formula_string:
                computed_formula_values[formula_field.id] = evaluate_formula(formula_field.options.formula_string, current_record_values_map, field_defs_map)
        final_value_dtos = [schemas.RecordValue.from_orm(rv) for rv in record_sa.values if rv.field.type != 'formula']
        for formula_field in formula_fields:
            res = computed_formula_values.get(formula_field.id)
            val_dict = {"id": -formula_field.id, "record_id": record_sa.id, "field_id": formula_field.id, "owner_id": record_sa.owner_id}
            if isinstance(res, (int,float)): val_dict["value_number"] = res
            else: val_dict["value_text"] = str(res) if res is not None else None
            final_value_dtos.append(schemas.RecordValue.model_validate(val_dict))
        processed_records_dto.append(schemas.Record(id=record_sa.id, table_id=record_sa.table_id, owner_id=record_sa.owner_id, created_at=record_sa.created_at, updated_at=record_sa.updated_at, values=final_value_dtos))
    return processed_records_dto


def get_record(db: Session, record_id: int, user_id: int): # ... (as before with permission checks and returning Pydantic model)
    db_record_sa = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not db_record_sa: raise HTTPException(status_code=404, detail="Record not found")
    permission = get_user_table_permission_level(db, table_id=db_record_sa.table_id, user_id=user_id)
    if not permission: raise HTTPException(status_code=403, detail="Not enough permissions")
    # ... (formula computation and Pydantic model construction as in get_records_by_table) ...
    table_fields = db.query(models.Field).filter(models.Field.table_id == db_record_sa.table_id).all()
    field_defs_map = {field.id: field for field in table_fields}; formula_fields = [f for f in table_fields if f.type == 'formula']
    current_record_values_map = {rv.field_id: rv for rv in db_record_sa.values}; computed_formula_values = {}
    for ff in formula_fields:
        if ff.options and ff.options.formula_string: computed_formula_values[ff.id] = evaluate_formula(ff.options.formula_string, current_record_values_map, field_defs_map)
    final_value_dtos = [schemas.RecordValue.from_orm(rv) for rv in db_record_sa.values if rv.field.type != 'formula']
    for ff in formula_fields:
        res = computed_formula_values.get(ff.id); val_dict = {"id": -ff.id, "record_id": db_record_sa.id, "field_id": ff.id, "owner_id": db_record_sa.owner_id}
        if isinstance(res, (int,float)): val_dict["value_number"] = res
        else: val_dict["value_text"] = str(res) if res is not None else None
        final_value_dtos.append(schemas.RecordValue.model_validate(val_dict))
    return schemas.Record(id=db_record_sa.id, table_id=db_record_sa.table_id, owner_id=db_record_sa.owner_id, created_at=db_record_sa.created_at, updated_at=db_record_sa.updated_at, values=final_value_dtos)

async def update_record(db: Session, record_id: int, record_data: schemas.RecordUpdate, user_id: int): # ... (as before with permission checks)
    manager = get_connection_manager()
    db_record_sa = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not db_record_sa: raise HTTPException(status_code=404, detail="Record not found")
    permission = get_user_table_permission_level(db, table_id=db_record_sa.table_id, user_id=user_id)
    if not permission or permission not in [PermissionLevel.ADMIN, PermissionLevel.EDITOR]: raise HTTPException(status_code=403, detail="Not enough permissions")
    if record_data.values is not None:
        db.query(models.RecordValue).filter(models.RecordValue.record_id == record_id).delete(synchronize_session=False)
        link_field_ids_in_update = []
        for field_id_str, value in record_data.values.items():
            field_id = int(field_id_str)
            db_field = db.query(models.Field).filter(models.Field.id == field_id, models.Field.table_id == db_record_sa.table_id).first()
            if not db_field or db_field.type == 'formula': continue
            value_columns = _map_value_to_record_value_columns(db_field.type, value)
            db.add(models.RecordValue(record_id=record_id, field_id=field_id, owner_id=user_id, **value_columns))
            if db_field.type == 'linkToRecord': link_field_ids_in_update.append(field_id)
        if link_field_ids_in_update:
            db.query(models.RecordLink).filter(models.RecordLink.source_record_id == record_id, models.RecordLink.source_field_id.in_(link_field_ids_in_update)).delete(synchronize_session=False)
            for field_id in link_field_ids_in_update:
                value = record_data.values.get(str(field_id))
                if isinstance(value, list):
                    for linked_id_val in value: # Renamed to avoid conflict
                        db.add(models.RecordLink(source_record_id=record_id, source_field_id=field_id, linked_record_id=int(linked_id_val), owner_id=user_id))
    from sqlalchemy.sql import func
    db_record_sa.updated_at = func.now()
    db.commit()
    updated_record_dto = get_record(db, record_id, user_id)
    await manager.broadcast_json_to_room({"event": "record_updated", "data": updated_record_dto.model_dump(exclude_none=True)}, f"table_{db_record_sa.table_id}")
    return updated_record_dto

async def delete_record(db: Session, record_id: int, user_id: int): # ... (as before with permission checks)
    manager = get_connection_manager()
    db_record_sa = db.query(models.Record).filter(models.Record.id == record_id).first()
    if not db_record_sa: raise HTTPException(status_code=404, detail="Record not found")
    permission = get_user_table_permission_level(db, table_id=db_record_sa.table_id, user_id=user_id)
    if not permission or permission not in [PermissionLevel.ADMIN, PermissionLevel.EDITOR]: raise HTTPException(status_code=403, detail="Not enough permissions")
    table_id_for_broadcast = db_record_sa.table_id
    db.delete(db_record_sa); db.commit()
    await manager.broadcast_json_to_room({"event": "record_deleted", "data": {"record_id": record_id, "table_id": table_id_for_broadcast}}, f"table_{table_id_for_broadcast}")
    return {"message": "Record deleted"}

# View CRUD operations
def create_table_view(db: Session, view_data: schemas.ViewCreate, table_id: int, user_id: int):
    db_table = db.query(models.Table).filter(models.Table.id == table_id, models.Table.owner_id == user_id).first()
    if not db_table: raise HTTPException(status_code=404, detail="Table not found or user does not have access")

    # Type specific validation
    config = view_data.config
    if view_data.type == 'form' and config.form_fields:
        configured_field_ids = [ff_conf.field_id for ff_conf in config.form_fields]
        valid_fields_count = db.query(models.Field.id).filter(models.Field.table_id == table_id, models.Field.id.in_(configured_field_ids)).count()
        if valid_fields_count != len(configured_field_ids): raise HTTPException(status_code=400, detail="Invalid field_ids in form_fields")
    elif view_data.type == 'kanban':
        if not config.stack_by_field_id: raise HTTPException(status_code=400, detail="stack_by_field_id required for Kanban")
        all_ids_to_check = [config.stack_by_field_id] + (config.card_fields or [])
        valid_fields = {f.id:f for f in db.query(models.Field).filter(models.Field.table_id == table_id, models.Field.id.in_(all_ids_to_check)).all()}
        if config.stack_by_field_id not in valid_fields: raise HTTPException(status_code=400, detail="stack_by_field_id is invalid")
        if valid_fields[config.stack_by_field_id].type not in ['singleSelect', 'text', 'boolean']: raise HTTPException(status_code=400, detail="stack_by_field_id type not suitable for Kanban")
        if config.card_fields and len(valid_fields) != len(all_ids_to_check): raise HTTPException(status_code=400, detail="Invalid field_id in card_fields")
    elif view_data.type == 'calendar':
        if not config.date_field_id or not config.event_title_field_id: raise HTTPException(status_code=400, detail="date_field_id and event_title_field_id required for Calendar")
        all_ids_to_check = [config.date_field_id, config.event_title_field_id] + ([config.end_date_field_id] if config.end_date_field_id else [])
        valid_fields = {f.id:f for f in db.query(models.Field).filter(models.Field.table_id == table_id, models.Field.id.in_(all_ids_to_check)).all()}
        if len(valid_fields) != len(set(all_ids_to_check)): raise HTTPException(status_code=400, detail="Invalid field_id in calendar config")
        if valid_fields[config.date_field_id].type not in ['date', 'createdTime', 'lastModifiedTime']: raise HTTPException(status_code=400, detail="date_field_id must be a date type")
        if config.end_date_field_id and valid_fields[config.end_date_field_id].type not in ['date', 'createdTime', 'lastModifiedTime']: raise HTTPException(status_code=400, detail="end_date_field_id must be a date type")

    db_view = models.View(**view_data.model_dump(), table_id=table_id, owner_id=user_id)
    db.add(db_view); db.commit(); db.refresh(db_view)
    return db_view

def update_view(db: Session, view_id: int, view_data: schemas.ViewUpdate, user_id: int):
    db_view = get_view(db, view_id=view_id, user_id=user_id)
    if view_data.name is not None: db_view.name = view_data.name
    if view_data.type is not None: db_view.type = view_data.type
    
    if view_data.config is not None:
        current_type = view_data.type or db_view.type
        config = view_data.config
        # Apply type-specific validation if config for that type is being set
        if current_type == 'form' and config.form_fields is not None:
            configured_field_ids = [ff_conf.field_id for ff_conf in config.form_fields]
            valid_fields_count = db.query(models.Field.id).filter(models.Field.table_id == db_view.table_id, models.Field.id.in_(configured_field_ids)).count()
            if valid_fields_count != len(configured_field_ids): raise HTTPException(status_code=400, detail="Invalid field_ids in form_fields for update")
        elif current_type == 'kanban':
            if config.stack_by_field_id is not None: # Check only if it's being set/updated
                all_ids_to_check = [config.stack_by_field_id] + (config.card_fields or db_view.config.get('card_fields', [])) # Merge with existing if partial
                valid_fields = {f.id:f for f in db.query(models.Field).filter(models.Field.table_id == db_view.table_id, models.Field.id.in_(all_ids_to_check)).all()}
                if config.stack_by_field_id not in valid_fields: raise HTTPException(status_code=400, detail="stack_by_field_id is invalid for update")
                if valid_fields[config.stack_by_field_id].type not in ['singleSelect', 'text', 'boolean']: raise HTTPException(status_code=400, detail="stack_by_field_id type not suitable for Kanban for update")
            if config.card_fields is not None:
                all_ids_to_check = [config.stack_by_field_id or db_view.config.get('stack_by_field_id')] + config.card_fields
                valid_fields_count = db.query(models.Field.id).filter(models.Field.table_id == db_view.table_id, models.Field.id.in_(list(set(all_ids_to_check)))).count() # set to remove duplicates before count
                if valid_fields_count != len(set(all_ids_to_check)): raise HTTPException(status_code=400, detail="Invalid field_id in card_fields for update")
        elif current_type == 'calendar':
            if config.date_field_id is not None or config.event_title_field_id is not None: # Check if relevant parts are being updated
                # ... (similar detailed validation as in create_table_view for calendar) ...
                pass

        # For partial updates of config, merge with existing config
        existing_config = schemas.ViewConfig.model_validate(db_view.config).model_dump(exclude_unset=True)
        updated_config_data = view_data.config.model_dump(exclude_unset=True)
        merged_config = {**existing_config, **updated_config_data}
        db_view.config = merged_config # Store the merged, validated config
    
    db.commit(); db.refresh(db_view)
    return db_view

def get_view(db: Session, view_id: int, user_id: int):
    db_view = db.query(models.View).filter(models.View.id == view_id).first()
    if not db_view: raise HTTPException(status_code=404, detail="View not found")
    permission = get_user_table_permission_level(db, table_id=db_view.table_id, user_id=user_id)
    if not permission or permission < PermissionLevel.VIEWER : 
        raise HTTPException(status_code=403, detail="User does not have access to this view's table")
    # If view owner is different from current_user, but current_user has table access, they can see it.
    # If stricter view ownership is needed (only owner of view can fetch it directly), add:
    # if db_view.owner_id != user_id: raise HTTPException(status_code=403, detail="User does not own this specific view")
    return db_view

def get_views_by_table(db: Session, table_id: int, user_id: int):
    permission = get_user_table_permission_level(db, table_id=table_id, user_id=user_id)
    if not permission or permission < PermissionLevel.VIEWER: 
        raise HTTPException(status_code=403, detail="Not enough permissions to access this table's views")
    return db.query(models.View).filter(models.View.table_id == table_id).all() # Show all views for table if user has table access

def delete_view(db: Session, view_id: int, user_id: int):
    db_view = get_view(db, view_id=view_id, user_id=user_id) # Handles checks
    # Further check: Only owner of the view or table admin (or base owner) should delete.
    # get_view currently checks if user has at least viewer permission on the table.
    # For delete, we need stricter: either view owner, or table admin.
    is_admin_or_base_owner = check_table_admin_or_base_owner(db, table_id=db_view.table_id, user_id=user_id)
    if db_view.owner_id != user_id and not is_admin_or_base_owner:
        raise HTTPException(status_code=403, detail="Not authorized to delete this view")
    db.delete(db_view); db.commit()
    return db_view

# Permission helpers and CRUD
from .permission_levels import PermissionLevel # Already imported

def check_table_admin_or_base_owner(db: Session, table_id: int, user_id: int) -> bool: # ... (as before)
    table_with_base_owner = db.query(models.Table).join(models.Base).filter(models.Table.id == table_id, models.Base.owner_id == user_id).first()
    if table_with_base_owner: return True
    permission = db.query(models.TablePermission).filter(models.TablePermission.table_id == table_id, models.TablePermission.user_id == user_id, models.TablePermission.permission_level == PermissionLevel.ADMIN).first()
    return permission is not None

def grant_table_permission(db: Session, table_id: int, target_user_id: int, permission_level: PermissionLevel, current_user_id: int): # ... (as before)
    if not check_table_admin_or_base_owner(db, table_id, current_user_id): raise HTTPException(status_code=403, detail="Not authorized to manage permissions")
    table = db.query(models.Table).filter_by(id=table_id).first()
    if table and table.base.owner_id == target_user_id: raise HTTPException(status_code=400, detail="Cannot change permission for the base owner.")
    permission = db.query(models.TablePermission).filter_by(table_id=table_id, user_id=target_user_id).first()
    if permission: permission.permission_level = permission_level.value
    else: permission = models.TablePermission(table_id=table_id, user_id=target_user_id, permission_level=permission_level.value); db.add(permission)
    db.commit(); db.refresh(permission)
    return permission

def revoke_table_permission(db: Session, table_id: int, target_user_id: int, current_user_id: int): # ... (as before)
    if not check_table_admin_or_base_owner(db, table_id, current_user_id): raise HTTPException(status_code=403, detail="Not authorized to manage permissions")
    table = db.query(models.Table).filter_by(id=table_id).first()
    if table and table.base.owner_id == target_user_id: raise HTTPException(status_code=400, detail="Cannot revoke permission from the base owner.")
    permission = db.query(models.TablePermission).filter_by(table_id=table_id, user_id=target_user_id).first()
    if not permission: raise HTTPException(status_code=404, detail="Permission entry not found")
    db.delete(permission); db.commit()
    return {"message": "Permission revoked"}

def get_user_table_permission_level(db: Session, table_id: int, user_id: int) -> Optional[PermissionLevel]: # ... (as before)
    table = db.query(models.Table).filter_by(id=table_id).first()
    if not table: return None 
    if table.base.owner_id == user_id: return PermissionLevel.ADMIN
    permission = db.query(models.TablePermission).filter_by(table_id=table_id, user_id=user_id).first()
    if permission: return PermissionLevel(permission.permission_level)
    return None

def get_table_permissions(db: Session, table_id: int, current_user_id: int): # ... (as before)
    if not check_table_admin_or_base_owner(db, table_id, current_user_id): raise HTTPException(status_code=403, detail="Not authorized to view permissions")
    return db.query(models.TablePermission).filter_by(table_id=table_id).all()
