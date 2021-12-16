from __future__ import annotations
from typing import Optional

from pydantic import BaseModel, Field

from .attributes import GlobalAttributes
from .group import Group
from .variable import Variable


class DatasetMeta(BaseModel):
    file_pattern: str = Field(description='Canonical filename pattern for this dataset')


class Dataset(BaseModel):
    class Config:
        title = 'FAAM Dataset Schema'

    meta: DatasetMeta
    attributes: GlobalAttributes
    groups: Optional[Group]
    variables: list[Variable]