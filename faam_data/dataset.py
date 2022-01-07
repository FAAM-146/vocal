from __future__ import annotations
from typing import Optional
import netCDF4

from pydantic import BaseModel, Field

from .dimension import Dimension
from .attributes import GlobalAttributes
from .group import Group
from .variable import Variable
from .training import global_data_hooks


class DatasetMeta(BaseModel):
    file_pattern: str = Field(description='Canonical filename pattern for this dataset')


class Dataset(BaseModel):
    class Config:
        title = 'FAAM Dataset Schema'

    meta: DatasetMeta
    attributes: GlobalAttributes
    dimensions: list[Dimension]
    groups: Optional[list[Group]]
    variables: list[Variable]

    def to_test_nc(self) -> None:
        nc_filename = 'test.nc'
        with netCDF4.Dataset(nc_filename, 'w') as nc:
            for dim in self.dimensions:
                dim.to_nc_container(nc)

            for var in self.variables:
                var.to_nc_container(nc)

            if self.groups is not None:
                for group in self.groups:
                    group.to_nc_container(nc)

            for attr, value in self.attributes:
                try:
                    value = global_data_hooks[attr](nc)
                except KeyError:
                    pass

                if value is None:
                    continue

                try:
                    if value.startswith('<') and value.endswith('>'):
                        try:
                            schema = self.attributes.schema()
                            value = schema['properties'][attr]['example']
                        except KeyError:
                            print(self.schema())
                            raise
                except AttributeError:
                    pass

                try:
                    attr = attr.decode()
                except AttributeError:
                    pass

                try:
                    setattr(nc, attr, value)
                except TypeError:
                    setattr(nc, attr, str(value))