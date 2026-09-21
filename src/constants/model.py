"""ORM-wide naming convention and shared ``MetaData`` for SQLModel tables."""

from sqlalchemy import MetaData
from sqlmodel import SQLModel

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

ORM_METADATA = MetaData(naming_convention=NAMING_CONVENTION)

SQLModel.metadata = ORM_METADATA
