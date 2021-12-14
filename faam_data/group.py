from __future__ import annotations
from typing import Optional

from pydantic import BaseModel

from .attributes import GroupAttributes
from .dimension import Dimension
from variable import Variable


class GroupMeta(BaseModel):
    class Config:
        title = 'Group Metadata'

    name: str

class Group(BaseModel):
    class Config:
        title = 'FAAM Group Schema'

    meta: GroupMeta
    attributes: GroupAttributes
    dimensions: list[Dimension]
    groups: Optional[list[Group]]
    variables: list[Variable]
    
Group.update_forward_refs()