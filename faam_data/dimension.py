from pydantic import BaseModel
from typing import Union


class Dimension(BaseModel):
    name: str
    size: Union[int, None]