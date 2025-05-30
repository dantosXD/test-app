from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/bases",
    tags=["bases"],
    dependencies=[Depends(auth.get_current_active_user)], # All routes in this router require authentication
)

@router.post("/", response_model=schemas.Base, status_code=status.HTTP_201_CREATED)
async def create_new_base(
    base: schemas.BaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return crud.create_base(db=db, base=base, owner_id=current_user.id)

@router.get("/", response_model=List[schemas.Base])
async def read_user_bases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    bases = crud.get_bases_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return bases

@router.get("/{base_id}", response_model=schemas.Base)
async def read_single_base(
    base_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_base = crud.get_base(db, base_id=base_id, owner_id=current_user.id)
    if db_base is None:
        raise HTTPException(status_code=404, detail="Base not found or not owned by user")
    return db_base

@router.put("/{base_id}", response_model=schemas.Base)
async def update_existing_base(
    base_id: int,
    base_update: schemas.BaseUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    updated_base = crud.update_base(db, base_id=base_id, base_update=base_update, owner_id=current_user.id)
    if updated_base is None:
        raise HTTPException(status_code=404, detail="Base not found or not owned by user")
    return updated_base

@router.delete("/{base_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_base(
    base_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    deleted_base = crud.delete_base(db, base_id=base_id, owner_id=current_user.id)
    if deleted_base is None: # crud.delete_base now returns the object if found, or None
        raise HTTPException(status_code=404, detail="Base not found or not owned by user")
    return None # Return None for 204 No Content
