from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db

router = APIRouter(
    tags=["records"],
    dependencies=[Depends(auth.get_current_active_user)],
)

@router.post("/tables/{table_id}/records", response_model=schemas.Record, status_code=status.HTTP_201_CREATED)
async def create_record_in_table_endpoint(
    table_id: int,
    record_data: schemas.RecordCreate, # Uses {field_id: value} dict
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.create_table_record handles table ownership check and record creation
    return crud.create_table_record(db=db, record_data=record_data, table_id=table_id, user_id=current_user.id)

from typing import Optional # Import Optional

@router.get("/tables/{table_id}/records", response_model=List[schemas.Record])
async def read_records_for_table_endpoint(
    table_id: int,
    skip: int = 0,
    limit: int = 100,
    sort_by_field_id: Optional[int] = None,
    sort_direction: Optional[str] = "asc", # Validate "asc" or "desc"
    filter_by_field_id: Optional[int] = None,
    filter_value: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if sort_direction not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort_direction. Must be 'asc' or 'desc'.")

    # crud.get_records_by_table handles table ownership check and other logic
    records = crud.get_records_by_table(
        db,
        table_id=table_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        sort_by_field_id=sort_by_field_id,
        sort_direction=sort_direction,
        filter_by_field_id=filter_by_field_id,
        filter_value=filter_value
    )
    return records

@router.get("/records/{record_id}", response_model=schemas.Record)
async def read_record_endpoint(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_record = crud.get_record(db, record_id=record_id, user_id=current_user.id)
    # crud.get_record raises HTTPException if not found or no access
    return db_record

@router.put("/records/{record_id}", response_model=schemas.Record)
async def update_record_endpoint(
    record_id: int,
    record_data: schemas.RecordUpdate, # Uses {field_id: value} dict
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    updated_record = crud.update_record(db, record_id=record_id, record_data=record_data, user_id=current_user.id)
    # crud.update_record raises HTTPException if not found or no access
    return updated_record

@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record_endpoint(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    deleted_record = crud.delete_record(db, record_id=record_id, user_id=current_user.id)
    # crud.delete_record raises HTTPException if not found or no access
    # If it returns the object, we just ensure it's not None (though exception should cover)
    if deleted_record is None:
         raise HTTPException(status_code=404, detail="Record not found or operation failed")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
