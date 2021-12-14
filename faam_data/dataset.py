from __future__ import annotations
from typing import Optional

from pydantic import BaseModel

from .attributes import GlobalAttributes
from .group import Group
from .variable import Variable


class Dataset(BaseModel):
    class Config:
        title = 'FAAM Dataset Schema'

    attributes: GlobalAttributes
    groups: Optional[Group]
    variables: list[Variable]