from __future__ import annotations

from pydantic import BaseModel
from typing import Optional

from faam_data.attributes import GlobalAttributes, GroupAttributes
from faam_data.variable import Variable
from faam_data.dimension import Dimension


class Group(BaseModel):
    class Config:
        title = 'FAAM Group Schema'

    attributes: GroupAttributes
    dimensions: list[Dimension]
    groups: list[Group]
    variables: list[Variable]
    
Group.update_forward_refs()


class Dataset(BaseModel):
    class Config:
        title = 'FAAM Dataset Schema'

    attributes: GlobalAttributes
    groups: Optional[Group]
    variables: list[Variable]