from pydantic import BaseModel, Field
from typing import List

from .attributes import VariableAttributes
from .dimension import Dimension

class VariableMeta(BaseModel):
    datatype: str = Field(description='The type of the data')
    name: str


class Variable(BaseModel):
    meta: VariableMeta
    dimensions: List[Dimension]
    attributes: VariableAttributes