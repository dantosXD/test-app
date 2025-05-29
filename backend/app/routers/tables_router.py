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
