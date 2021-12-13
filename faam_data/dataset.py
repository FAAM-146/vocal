from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional

from faam_data.attributes import GlobalAttributes, GroupAttributes
from faam_data.variable import Variable


class Group(BaseModel):
    class Config:
        title = 'FAAM Group Schema'

    attributes: GroupAttributes
    groups: List[Group]
    variables: List[Variable]
    
Group.update_forward_refs()


class Dataset(BaseModel):
    class Config:
        title = 'FAAM Dataset Schema'

    attributes: GlobalAttributes
    groups: Optional[Group]
    variables: List[Variable]


print(Group.schema_json())