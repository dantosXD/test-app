from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    bases = relationship("Base", back_populates="owner")

class Base(Base):
    __tablename__ = "bases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)

    owner = relationship("User", back_populates="bases")
    tables = relationship("Table", back_populates="base", cascade="all, delete-orphan") # This is AppBase -> Table

class User(Base): # Ensure User model is updated if not already defined like this
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    bases = relationship("Base", back_populates="owner")
    tables = relationship("Table", back_populates="owner") # User -> Table relationship
    fields = relationship("Field", back_populates="owner") # User -> Field relationship
    records = relationship("Record", back_populates="owner") # User -> Record relationship
    record_values = relationship("RecordValue", back_populates="owner") # User -> RecordValue relationship

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base_id = Column(Integer, ForeignKey("bases.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True) # Added owner_id
    name = Column(String, nullable=False)

    base = relationship("Base", back_populates="tables") # Table -> AppBase relationship
    owner = relationship("User", back_populates="tables") # Table -> User relationship
    fields = relationship("Field", back_populates="table", cascade="all, delete-orphan") # Table -> Field relationship (already exists)
    records = relationship("Record", back_populates="table", cascade="all, delete-orphan")

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True) # Added owner_id
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'text', 'number', 'date', 'boolean', 'singleSelect', 'multiSelect', 'attachment', 'email', 'url'
    options = Column(JSON, nullable=True) # For field-specific options like select choices

    table = relationship("Table", back_populates="fields") # Field -> Table relationship (already exists)
    owner = relationship("User", back_populates="fields") # Field -> User relationship
    record_values = relationship("RecordValue", back_populates="field", cascade="all, delete-orphan") # Field -> RecordValue relationship (already exists)

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True) # Added owner_id
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    table = relationship("Table", back_populates="records") # Record -> Table relationship (already exists)
    owner = relationship("User", back_populates="records") # Record -> User relationship
    values = relationship("RecordValue", back_populates="record", cascade="all, delete-orphan") # Record -> RecordValue relationship

class RecordValue(Base):
    __tablename__ = "record_values"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("records.id"), nullable=False, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True) # Added owner_id
    
    value_text = Column(Text, nullable=True)
    value_number = Column(Float, nullable=True)
    value_boolean = Column(Boolean, nullable=True)
    value_datetime = Column(DateTime(timezone=True), nullable=True)
    value_json = Column(JSON, nullable=True) # For select types, attachments, or other complex data

    record = relationship("Record", back_populates="values") # RecordValue -> Record relationship
    field = relationship("Field", back_populates="record_values") # RecordValue -> Field relationship (already exists)
    owner = relationship("User", back_populates="record_values") # RecordValue -> User relationship

    __table_args__ = (
        # Potentially add unique constraint for (record_id, field_id) if needed
        # UniqueConstraint('record_id', 'field_id', name='uq_record_field'),
    )
