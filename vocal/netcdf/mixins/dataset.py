from __future__ import annotations
import os
import tempfile
import netCDF4 # type: ignore
import pydantic
import numpy.typing
from typing import Optional, Protocol
from collections.abc import Generator

from contextlib import contextmanager

from ...training import global_data_hooks
from ...utils import get_type_from_placeholder
from .protocols import HasDatasetAttributes



class DatasetNetCDFMixin:

    @contextmanager
    def create_example_file(
        self: HasDatasetAttributes, nc_filename: str, coordinates: Optional[str]=None
    ) -> Generator[netCDF4.Dataset, None, None]:
        
        with netCDF4.Dataset(nc_filename, 'w') as nc:
            for dim in self.dimensions:
                dim.to_nc_container(nc)

            for var in self.variables:
                var.to_nc_container(nc, coordinates)

            if self.groups is not None:
                for group in self.groups:
                    group.to_nc_container(nc) 

            for attr, value in self.attributes:
                try:
                    value = global_data_hooks[attr](nc=nc, attrs=self.attributes) 
                except KeyError:
                    pass

                if value is None:
                    continue

                try:
                    setattr(nc, attr, value)
                except TypeError:
                    setattr(nc, attr, str(value))

            yield nc
            

    def tocdl(self: HasDatasetAttributes, filename: str | None=None) -> str:
        """
        Convert the dataset to CDL.

        Returns:
            str: The CDL representation of the dataset.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            ncfile = os.path.join(tmpdir, 'temp.nc')
            with netCDF4.Dataset(ncfile, 'w') as nc:
                for dim in self.dimensions:
                    dim.to_nc_container(nc) 

                for var in self.variables:
                    var.to_nc_container(
                        nc=nc,
                        coordinates=None,
                        populate=False
                    ) 

                if self.groups is not None:
                    for group in self.groups:
                        group.to_nc_container(nc=nc, populate=False) 

                for attr, value in self.attributes:
                    try:
                        value = global_data_hooks[attr](nc=nc, attrs=self.attributes)
                    except KeyError:
                        pass

                    if value is None:
                        continue

                    try:
                        setattr(nc, attr, value)
                    except TypeError:
                        setattr(nc, attr, str(value))

            with netCDF4.Dataset(ncfile, 'r') as nc:
                cdl = nc.tocdl()

        if filename is not None:
            with open(filename, 'w') as f:
                f.write(cdl)
        
        return cdl