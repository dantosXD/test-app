from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .config import settings
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # Adjusted tokenUrl to match router prefix

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    # if current_user.disabled: # If you add a disabled field to user model
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# New permission dependency
from .permission_levels import PermissionLevel # Import Enum

def verify_user_table_access(
    table_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_user),
    required_level: PermissionLevel = PermissionLevel.VIEWER # Default to viewer
) -> models.Table:
    permission = crud.get_user_table_permission_level(db, table_id=table_id, user_id=current_user.id)
    
    if not permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this table (no entry)")

    # Define hierarchy: ADMIN > EDITOR > VIEWER
    if required_level == PermissionLevel.ADMIN and permission != PermissionLevel.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permission required")
    if required_level == PermissionLevel.EDITOR and permission not in [PermissionLevel.ADMIN, PermissionLevel.EDITOR]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Editor or Admin permission required")
    # VIEWER level is implicitly covered if any permission exists.

    # Return the table if access is granted, routers might need it
    table = db.query(models.Table).filter(models.Table.id == table_id).first()
    if not table: # Should not happen if permission check passed and table_id is valid
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    return table
