from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, crud, models, schemas
from ..database import get_db
from ..permission_levels import PermissionLevel

router = APIRouter(
    prefix="/tables/{table_id}/permissions",
    tags=["table_permissions"],
    dependencies=[Depends(auth.get_current_active_user)],
)

class TablePermissionResponse(schemas.BaseModel): # Using Pydantic BaseModel for response
    user_id: int
    email: str # Include email for easier identification on frontend
    permission_level: PermissionLevel

    class Config:
        from_attributes = True


class GrantPermissionRequest(schemas.BaseModel):
    user_email: schemas.EmailStr
    permission_level: PermissionLevel


@router.post("/", response_model=TablePermissionResponse)
async def grant_permission_for_table(
    table_id: int,
    request: GrantPermissionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    target_user = crud.get_user_by_email(db, email=request.user_email)
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User with email {request.user_email} not found")

    permission_sa = crud.grant_table_permission(
        db=db,
        table_id=table_id,
        target_user_id=target_user.id,
        permission_level=request.permission_level,
        current_user_id=current_user.id
    )
    return TablePermissionResponse(
        user_id=target_user.id,
        email=target_user.email,
        permission_level=PermissionLevel(permission_sa.permission_level) # Ensure it's enum
    )


@router.delete("/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_permission_for_table(
    table_id: int,
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    crud.revoke_table_permission(
        db=db,
        table_id=table_id,
        target_user_id=target_user_id,
        current_user_id=current_user.id
    )
    from fastapi import Response # Ensure Response is imported
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/", response_model=List[TablePermissionResponse])
async def list_permissions_for_table(
    table_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    permissions_sa_list = crud.get_table_permissions(db=db, table_id=table_id, current_user_id=current_user.id)

    response_list = []
    for perm_sa in permissions_sa_list:
        # perm_sa.user should be loaded if relationship is set up correctly, or fetch user
        user_email = perm_sa.user.email if perm_sa.user else "Unknown" # Fallback, ideally user always exists
        if not perm_sa.user: # If user somehow not loaded/deleted, fetch manually
            user_model = crud.get_user(db, user_id=perm_sa.user_id)
            if user_model: user_email = user_model.email

        response_list.append(TablePermissionResponse(
            user_id=perm_sa.user_id,
            email=user_email,
            permission_level=PermissionLevel(perm_sa.permission_level)
        ))
    return response_list
