from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db

router = APIRouter(
    # prefix="/tables", # Individual routes will specify full path for now (e.g. /bases/{base_id}/tables)
    tags=["tables"],
    dependencies=[Depends(auth.get_current_active_user)],
)

@router.post("/bases/{base_id}/tables", response_model=schemas.Table, status_code=status.HTTP_201_CREATED)
async def create_table_for_base_endpoint(
    base_id: int,
    table: schemas.TableCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.create_base_table will check if base exists and if user owns it
    return crud.create_base_table(db=db, table=table, base_id=base_id, user_id=current_user.id)

@router.get("/bases/{base_id}/tables", response_model=List[schemas.Table])
async def read_tables_for_base_endpoint(
    base_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.get_tables_by_base will check if base exists and if user owns it
    tables = crud.get_tables_by_base(db, base_id=base_id, user_id=current_user.id, skip=skip, limit=limit)
    return tables

@router.get("/tables/{table_id}", response_model=schemas.Table)
async def read_table_endpoint(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_table = crud.get_table(db, table_id=table_id, user_id=current_user.id)
    if db_table is None: # This check is also in crud.get_table, but good for clarity
        raise HTTPException(status_code=404, detail="Table not found or insufficient permissions")
    return db_table

@router.put("/tables/{table_id}", response_model=schemas.Table)
async def update_table_endpoint(
    table_id: int,
    table_update: schemas.TableUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    updated_table = crud.update_table(db, table_id=table_id, table_update=table_update, user_id=current_user.id)
    if updated_table is None: # This check is also in crud.update_table
        raise HTTPException(status_code=404, detail="Table not found or insufficient permissions")
    return updated_table

@router.delete("/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table_endpoint(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    deleted_table = crud.delete_table(db, table_id=table_id, user_id=current_user.id)
    if deleted_table is None: # crud.delete_table returns the object or raises if not found
        # This case should ideally be handled by the exception in crud.delete_table
        raise HTTPException(status_code=404, detail="Table not found or insufficient permissions")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

import csv
import io
from starlette.responses import StreamingResponse
from typing import Optional # For Optional type hint in format_value_for_csv if RecordValue can be None
from ..permission_levels import PermissionLevel


def format_value_for_csv(value_obj: Optional[schemas.RecordValue], field_type: str) -> str:
    if not value_obj:
        return ""

    if field_type == 'text' or field_type == 'singleSelect' or field_type == 'email' or field_type == 'url' or field_type == 'phoneNumber':
        return value_obj.value_text if value_obj.value_text is not None else ""
    elif field_type == 'number' or field_type == 'count':
        return str(value_obj.value_number) if value_obj.value_number is not None else ""
    elif field_type == 'boolean':
        return "TRUE" if value_obj.value_boolean else "FALSE" if value_obj.value_boolean is not None else ""
    elif field_type == 'date' or field_type == 'createdTime' or field_type == 'lastModifiedTime':
        return value_obj.value_datetime.isoformat() if value_obj.value_datetime else ""
    elif field_type == 'multiSelect' or field_type == 'linkToRecord': # list of strings or list of ints
        # For linkToRecord, value_json contains list of ints. For multiSelect, list of strings.
        return ",".join(map(str, value_obj.value_json)) if value_obj.value_json and isinstance(value_obj.value_json, list) else ""
    elif field_type == 'attachment': # list of dicts
        if value_obj.value_json and isinstance(value_obj.value_json, list):
            return ";".join([att.get('original_filename', 'file') for att in value_obj.value_json]) # Semicolon separated filenames
        return ""
    elif field_type == 'formula': # Computed value, stored in value_number or value_text by CRUD
        return str(value_obj.value_number) if value_obj.value_number is not None else (value_obj.value_text if value_obj.value_text is not None else "")
    return ""


@router.get("/{table_id}/export_csv")
async def export_table_to_csv(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verify user has at least viewer permission for the table
    permission = crud.get_user_table_permission_level(db, table_id=table_id, user_id=current_user.id)
    if not permission or permission < PermissionLevel.VIEWER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to export this table")

    table = db.query(models.Table).filter(models.Table.id == table_id).first() # No ownership check needed here, covered by permission
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    fields = db.query(models.Field).filter(models.Field.table_id == table_id).order_by(models.Field.id).all()
    # get_records_by_table returns Pydantic models with computed formulas
    # Fetch all records for export, consider pagination/streaming for very large tables in future
    records_data = crud.get_records_by_table(db, table_id=table_id, user_id=current_user.id, limit=1000000)

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row: Record ID + Field Names
    header = ["record_id"] + [field.name for field in fields]
    writer.writerow(header)

    # Data rows
    for record_dto in records_data: # record_dto is schemas.Record
        row = [str(record_dto.id)]
        values_map = {val.field_id: val for val in record_dto.values} # Map field_id to Pydantic RecordValue
        for field in fields:
            value_obj = values_map.get(field.id) # This is a schemas.RecordValue instance
            row.append(format_value_for_csv(value_obj, field.type))
        writer.writerow(row)

    output.seek(0)
    response = StreamingResponse(output, media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=table_{table.name.replace(' ','_')}_{table_id}_export.csv"
    return response


@router.post("/{table_id}/import_csv")
async def import_csv_to_table(
    table_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Verify user has at least editor permission for the table
    permission = crud.get_user_table_permission_level(db, table_id=table_id, user_id=current_user.id)
    if not permission or permission < PermissionLevel.EDITOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to import data to this table")

    table = db.query(models.Table).filter(models.Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    # Read and parse CSV content
    contents = await file.read()
    try:
        csv_data = io.StringIO(contents.decode('utf-8-sig')) # Handle UTF-8 with BOM
    except UnicodeDecodeError:
        try: # Fallback to latin-1 if utf-8 fails
            csv_data = io.StringIO(contents.decode('latin-1'))
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Failed to decode CSV. Please ensure it's UTF-8 or Latin-1 encoded.")

    reader = csv.DictReader(csv_data)

    table_fields = db.query(models.Field).filter(models.Field.table_id == table_id).all()
    # Map field names to their Field objects for quick lookup and type info
    # For simplicity, assume CSV headers match Field.name exactly (case-sensitive for now)
    field_map = {field.name: field for field in table_fields if field.type != 'formula'} # Exclude formula fields

    success_count = 0
    error_count = 0
    errors = []

    for row_idx, row_dict in enumerate(reader):
        record_values_payload: Dict[int, Any] = {}
        valid_row = True

        for header_name, cell_value_str in row_dict.items():
            field = field_map.get(header_name)
            if not field: # Column in CSV not found as a field in the table or is a formula field
                # Optionally log this or allow ignoring unknown columns
                continue

            # Basic type conversion attempt (more robust validation can be added)
            # crud._map_value_to_record_value_columns expects correctly typed values for some types (like list for multiSelect)
            # For CSV, all values are strings initially.

            typed_value: Any = cell_value_str # Default to string

            if cell_value_str is None or cell_value_str == "": # Treat empty strings as None for nullable fields
                typed_value = None
            elif field.type == 'number' or field.type == 'count':
                try: typed_value = float(cell_value_str)
                except ValueError: errors.append({"row": row_idx + 2, "field": header_name, "error": "Invalid number format"}); valid_row = False; break
            elif field.type == 'boolean':
                typed_value = cell_value_str.lower() in ['true', '1', 'yes', 't']
            elif field.type == 'date' or field.type == 'createdTime' or field.type == 'lastModifiedTime':
                # Expect ISO format or let Pydantic/SQLAlchemy handle it if possible.
                # For now, pass as string. More robust parsing needed for various date formats.
                typed_value = cell_value_str
            elif field.type == 'multiSelect' or field.type == 'linkToRecord':
                # Expect comma-separated string, convert to list of strings/ints
                items = [item.strip() for item in cell_value_str.split(',') if item.strip()]
                if field.type == 'linkToRecord':
                    try: typed_value = [int(item) for item in items]
                    except ValueError: errors.append({"row": row_idx + 2, "field": header_name, "error": "Invalid list of IDs for linkToRecord"}); valid_row = False; break
                else: # multiSelect
                    typed_value = items
            elif field.type == 'attachment': # Expect semi-colon separated list of filenames or JSON string
                # For simplicity, import won't create attachments from filenames.
                # Expects JSON string of metadata list, or skip. For now, skip complex parsing.
                typed_value = None # Or parse if a specific format is defined for CSV import

            if valid_row:
                record_values_payload[field.id] = typed_value

        if not valid_row:
            error_count += 1
            continue

        if not record_values_payload: # Skip empty rows or rows with no matching headers
            errors.append({"row": row_idx + 2, "error": "No data found for any known fields in this row."})
            error_count += 1
            continue

        record_create_schema = schemas.RecordCreate(values=record_values_payload)
        try:
            # Using current_user.id as owner of imported records
            await crud.create_table_record(
                db=db,
                record_data=record_create_schema,
                table_id=table_id,
                user_id=current_user.id # Or table.owner_id if preferred for imported data
            )
            success_count += 1
        except HTTPException as he: # Catch HTTPExceptions from CRUD if any validation fails there
            errors.append({"row": row_idx + 2, "error": f"HTTP {he.status_code}: {he.detail}"})
            error_count += 1
        except ValueError as ve: # Catch ValueErrors from _map_value_to_record_value_columns
             errors.append({"row": row_idx + 2, "error": str(ve)})
             error_count += 1
        except Exception as e:
            errors.append({"row": row_idx + 2, "error": f"An unexpected error occurred: {str(e)}"})
            error_count += 1
            # For critical errors, might re-raise or stop processing.

    return {
        "message": f"CSV import completed. {success_count} records imported, {error_count} rows failed.",
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors,
    }
