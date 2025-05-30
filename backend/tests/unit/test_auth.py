import pytest
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from app.auth import create_access_token, get_password_hash, verify_password
# Assuming app.models and app.crud might be needed for get_current_user, but not for these direct utils
# from app import models, crud, schemas
from app.config import settings # For SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def test_get_and_verify_password():
    password = "testpassword"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrongpassword", hashed_password) is False
    assert verify_password(password, "notarealhash") is False # Test against an invalid hash

def test_create_access_token_basic():
    data = {"sub": "testuser@example.com"}
    token = create_access_token(data) # Use default expires_delta
    assert token is not None

    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_token["sub"] == "testuser@example.com"
    assert "exp" in decoded_token
    # Check if default expiration is roughly correct (e.g., within a few seconds of expected)
    expected_exp = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assert abs(decoded_token["exp"] - int(expected_exp.timestamp())) < 5 # Allow 5s diff

def test_create_access_token_custom_expiry():
    data = {"sub": "anotheruser@example.com"}
    custom_delta = timedelta(hours=1)
    token = create_access_token(data, expires_delta=custom_delta)
    assert token is not None

    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_token["sub"] == "anotheruser@example.com"
    expected_exp = datetime.now(timezone.utc) + custom_delta
    assert abs(decoded_token["exp"] - int(expected_exp.timestamp())) < 5

def test_create_access_token_no_sub():
    # While 'sub' is standard, the function itself doesn't mandate it in data dict
    data = {"user_id": 123, "role": "admin"}
    token = create_access_token(data)
    assert token is not None
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_token["user_id"] == 123
    assert decoded_token["role"] == "admin"

# Note: Testing get_current_user and verify_user_table_access would typically be
# integration tests as they depend on DB access (via crud) and FastAPI Depends.
# These could be mocked for unit tests, but that's more involved.
# For now, focusing on the utility functions in auth.py.
