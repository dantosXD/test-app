from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db

router = APIRouter(
    tags=["views"],
    dependencies=[Depends(auth.get_current_active_user)],
)

@router.post("/tables/{table_id}/views", response_model=schemas.View, status_code=status.HTTP_201_CREATED)
async def create_view_for_table_endpoint(
    table_id: int,
    view_data: schemas.ViewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.create_table_view handles table ownership check
    return crud.create_table_view(db=db, view_data=view_data, table_id=table_id, user_id=current_user.id)

@router.get("/tables/{table_id}/views", response_model=List[schemas.View])
async def read_views_for_table_endpoint(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.get_views_by_table handles table ownership check
    return crud.get_views_by_table(db=db, table_id=table_id, user_id=current_user.id)

@router.get("/views/{view_id}", response_model=schemas.View)
async def read_view_endpoint(
    view_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.get_view handles ownership check
    db_view = crud.get_view(db=db, view_id=view_id, user_id=current_user.id)
    if db_view is None: # Should be handled by crud.get_view raising exception
        raise HTTPException(status_code=404, detail="View not found or insufficient permissions")
    return db_view

@router.put("/views/{view_id}", response_model=schemas.View)
async def update_view_endpoint(
    view_id: int,
    view_data: schemas.ViewUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.update_view handles ownership check
    updated_view = crud.update_view(db=db, view_id=view_id, view_data=view_data, user_id=current_user.id)
    if updated_view is None: # Should be handled by crud.update_view
        raise HTTPException(status_code=404, detail="View not found or insufficient permissions for update")
    return updated_view

@router.delete("/views/{view_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_view_endpoint(
    view_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # crud.delete_view handles ownership check
    deleted_view = crud.delete_view(db=db, view_id=view_id, user_id=current_user.id)
    if deleted_view is None: # Should be handled by crud.delete_view
         raise HTTPException(status_code=404, detail="View not found or insufficient permissions for delete")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
