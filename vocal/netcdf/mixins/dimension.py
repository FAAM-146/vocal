import netCDF4 # type: ignore
from typing import Protocol, Union


class HasDimensionAttributes(Protocol):
    name: str
    size: Union[int, None]


class DimensionNetCDFMixin:

    def to_nc_container(self: HasDimensionAttributes, nc: netCDF4.Dataset) -> None:
        nc.createDimension(self.name, self.size)