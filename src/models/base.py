"""Base helpers for all SQLModel models."""

from sqlmodel import SQLModel

from src.constants.model import ORM_METADATA

SQLModel.metadata = ORM_METADATA

Base = SQLModel
