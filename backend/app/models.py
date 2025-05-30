from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, JSON, Text, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base as DeclarativeBase # Use an alias for clarity

class User(DeclarativeBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    bases = relationship("AppBase", back_populates="owner") # Changed "Base" to "AppBase"
    tables = relationship("Table", back_populates="owner")
    fields = relationship("Field", back_populates="owner")
    records = relationship("Record", back_populates="owner")
    record_values = relationship("RecordValue", back_populates="owner")
    views = relationship("View", back_populates="owner")
    record_links = relationship("RecordLink", back_populates="owner")
    table_permissions = relationship("TablePermission", back_populates="user")

class AppBase(DeclarativeBase): # Renamed from Base to AppBase
    __tablename__ = "app_bases" # Changed tablename to avoid conflict if 'bases' was problematic

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)

    owner = relationship("User", back_populates="bases")
    tables = relationship("Table", back_populates="base", cascade="all, delete-orphan")

class Table(DeclarativeBase):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    base_id = Column(Integer, ForeignKey("app_bases.id"), nullable=False, index=True) # Changed from "bases.id"
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)

    base = relationship("AppBase", back_populates="tables") # Changed from "Base"
    owner = relationship("User", back_populates="tables")
    fields = relationship("Field", back_populates="table", cascade="all, delete-orphan")
    records = relationship("Record", back_populates="table", cascade="all, delete-orphan")
    views = relationship("View", back_populates="table", cascade="all, delete-orphan")
    user_permissions = relationship("TablePermission", back_populates="table", cascade="all, delete-orphan")

class Field(DeclarativeBase):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    options = Column(JSON, nullable=True)

    table = relationship("Table", back_populates="fields")
    owner = relationship("User", back_populates="fields")
    record_values = relationship("RecordValue", back_populates="field", cascade="all, delete-orphan")
    record_links = relationship("RecordLink", foreign_keys="RecordLink.source_field_id", back_populates="source_field", cascade="all, delete-orphan")

class Record(DeclarativeBase):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    table = relationship("Table", back_populates="records")
    owner = relationship("User", back_populates="records")
    values = relationship("RecordValue", back_populates="record", cascade="all, delete-orphan")
    initiated_links = relationship("RecordLink", foreign_keys="RecordLink.source_record_id", back_populates="source_record", cascade="all, delete-orphan")
    linked_to_this_record = relationship("RecordLink", foreign_keys="RecordLink.linked_record_id", back_populates="linked_record", cascade="all, delete-orphan")

class RecordValue(DeclarativeBase):
    __tablename__ = "record_values"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(Integer, ForeignKey("records.id"), nullable=False, index=True)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    value_text = Column(Text, nullable=True)
    value_number = Column(Float, nullable=True)
    value_boolean = Column(Boolean, nullable=True)
    value_datetime = Column(DateTime(timezone=True), nullable=True)
    value_json = Column(JSON, nullable=True)

    record = relationship("Record", back_populates="values")
    field = relationship("Field", back_populates="record_values")
    owner = relationship("User", back_populates="record_values")

    __table_args__ = (
        UniqueConstraint('record_id', 'field_id', name='uq_record_value_record_field'),
    )

class View(DeclarativeBase):
    __tablename__ = "views"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, default='grid', nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    config = Column(JSON, nullable=False)

    owner = relationship("User", back_populates="views")
    table = relationship("Table", back_populates="views")

class RecordLink(DeclarativeBase):
    __tablename__ = "record_links"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_record_id = Column(Integer, ForeignKey("records.id"), nullable=False, index=True)
    source_field_id = Column(Integer, ForeignKey("fields.id"), nullable=False, index=True)
    linked_record_id = Column(Integer, ForeignKey("records.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    source_record = relationship("Record", foreign_keys="RecordLink.source_record_id", back_populates="initiated_links")
    linked_record = relationship("Record", foreign_keys="RecordLink.linked_record_id", back_populates="linked_to_this_record")
    source_field = relationship("Field", foreign_keys="RecordLink.source_field_id", back_populates="record_links")
    owner = relationship("User", back_populates="record_links")

    __table_args__ = (
        UniqueConstraint('source_record_id', 'source_field_id', 'linked_record_id', name='uq_record_link_constraint'),
    )

class TablePermission(DeclarativeBase):
    __tablename__ = "table_permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False, index=True)
    permission_level = Column(String, nullable=False)

    user = relationship("User", back_populates="table_permissions")
    table = relationship("Table", back_populates="user_permissions")

    __table_args__ = (
        UniqueConstraint('user_id', 'table_id', name='uq_user_table_permission'),
    )
