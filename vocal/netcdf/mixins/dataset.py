from __future__ import annotations
import netCDF4 # type: ignore
import pydantic
import numpy.typing
from typing import Optional, Protocol

from ...training import global_data_hooks
from ...utils import get_type_from_placeholder

class HasDatasetMeta(Protocol):
    file_pattern: str


class HasDatasetAttributes(Protocol):
    attributes: pydantic.BaseModel
    variables: list[pydantic.BaseModel]
    dimensions: list[pydantic.BaseModel]
    groups: list[pydantic.BaseModel]
    meta: HasDatasetMeta
    np_type: numpy.typing.DTypeLike


class DatasetNetCDFMixin:

    def create_example_file(
        self: HasDatasetAttributes, nc_filename: str, coordinates: Optional[str]=None
    ) -> None:
        
        with netCDF4.Dataset(nc_filename, 'w') as nc:
            for dim in self.dimensions:
                dim.to_nc_container(nc) # type: ignore

            for var in self.variables:
                var.to_nc_container(nc, coordinates) # type: ignore

            if self.groups is not None:
                for group in self.groups:
                    group.to_nc_container(nc) # type: ignore

            for attr, value in self.attributes:
                try:
                    value = global_data_hooks[attr](nc=nc, attrs=self.attributes) # type: ignore
                except KeyError:
                    pass

                if value is None:
                    continue

                try:
                    setattr(nc, attr, value)
                except TypeError:
                    setattr(nc, attr, str(value))