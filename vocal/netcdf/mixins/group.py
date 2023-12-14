from __future__ import annotations
from typing import Optional
from netCDF4 import Dataset # type: ignore

from .protocols import HasGroupAttributes

class GroupNetCDFMixin:

    def to_nc_container(self: HasGroupAttributes, nc: Dataset, populate: Optional[bool]=True) -> None:
        this_group = nc.createGroup(self.meta.name)

        for dim in self.dimensions:
            dim.to_nc_container(this_group)

        if self.groups is not None:
            for group in self.groups:
                group.to_nc_container(this_group)

        for var in self.variables:
            var.to_nc_container(this_group, coordinates=None, populate=populate)

        for attr, value in self.attributes:
            if value is None:
                continue
            
            try:
                setattr(this_group, attr, value)
            except TypeError:
                setattr(this_group, attr, str(value))