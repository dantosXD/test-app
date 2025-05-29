from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db

router = APIRouter(
    tags=["fields"],
    dependencies=[Depends(auth.get_current_active_user)],
)

@router.post("/tables/{table_id}/fields", response_model=schemas.Field, status_code=status.HTTP_201_CREATED)
async def create_field_for_table_endpoint(
    table_id: int,
    field: schemas.FieldCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.create_table_field will check if table exists and if user owns it
    return crud.create_table_field(db=db, field=field, table_id=table_id, user_id=current_user.id)

@router.get("/tables/{table_id}/fields", response_model=List[schemas.Field])
async def read_fields_for_table_endpoint(
    table_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.get_fields_by_table will check if table exists and if user owns it
    fields = crud.get_fields_by_table(db, table_id=table_id, user_id=current_user.id, skip=skip, limit=limit)
    return fields

@router.get("/fields/{field_id}", response_model=schemas.Field)
async def read_field_endpoint(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_field = crud.get_field(db, field_id=field_id, user_id=current_user.id)
    # This check is also in crud.get_field, but included for robustness / explicitness at router level
    if db_field is None: 
        raise HTTPException(status_code=404, detail="Field not found or insufficient permissions")
    return db_field

@router.put("/fields/{field_id}", response_model=schemas.Field)
async def update_field_endpoint(
    field_id: int,
    field_update: schemas.FieldUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    updated_field = crud.update_field(db, field_id=field_id, field_update=field_update, user_id=current_user.id)
    # This check is also in crud.update_field
    if updated_field is None: 
        raise HTTPException(status_code=404, detail="Field not found or insufficient permissions")
    return updated_field

@router.delete("/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field_endpoint(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    deleted_field = crud.delete_field(db, field_id=field_id, user_id=current_user.id)
    # This check is also in crud.delete_field
    if deleted_field is None: 
        raise HTTPException(status_code=404, detail="Field not found or insufficient permissions")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
