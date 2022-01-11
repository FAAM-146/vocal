from __future__ import annotations
from typing import Optional

from pydantic import BaseModel

from .dimension import Dimension
from .variable import Variable
from .attributes import AttributesSet


class GroupMeta(BaseModel):
    class Config:
        title = 'Group Metadata'

    name: str

class Group(BaseModel):
    class Config:
        title = 'FAAM Group Schema'

    meta: GroupMeta
    attributes: AttributesSet
    dimensions: Optional[list[Dimension]]
    groups: Optional[list[Group]]
    variables: list[Variable]

    def to_nc_container(self, nc):
        this_group = nc.createGroup(self.meta.name)

        if self.groups is not None:
            for group in self.groups:
                group.to_nc_container(this_group)

        for var in self.variables:
            var.to_nc_container(this_group)

        for attr, value in self.attributes:
            if value is None:
                continue
            
            try:
                setattr(this_group, attr, value)
            except TypeError:
                setattr(this_group, attr, str(value))
    
Group.update_forward_refs()