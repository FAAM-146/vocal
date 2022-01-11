import netCDF4 # type: ignore
from pydantic import BaseModel
from typing import Union


class Dimension(BaseModel):
    name: str
    size: Union[int, None]

    def to_nc_container(self, nc: netCDF4.Dataset) -> None:
        print(f'Creating dimension {self.name}')
        nc.createDimension(self.name, self.size)