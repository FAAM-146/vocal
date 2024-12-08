from __future__ import annotations
import os
import tempfile
import netCDF4  # type: ignore
from typing import Optional
from collections.abc import Generator

from contextlib import contextmanager

from ...training import global_data_hooks
from .protocols import HasDatasetAttributes


class DatasetNetCDFMixin:

    @contextmanager
    def _create_file(
        self: HasDatasetAttributes,
        nc_filename: str,
        coordinates: Optional[str] = None,
        populate: bool = True,
    ) -> Generator[netCDF4.Dataset, None, None]:
        """
        A context manager to create a netCDF file with the dataset's attributes, dimensions, variables, and groups.

        Args:
            nc_filename (str): The filename of the netCDF file to create.
            coordinates (Optional[str], optional): The name of the coordinate variable to use for the variables. Defaults to None.
            populate (bool, optional): Whether to populate the variables with data. Defaults to True.

        Yields:
            Generator[netCDF4.Dataset, None, None]: The created netCDF file.
        """

        with netCDF4.Dataset(nc_filename, "w") as nc:
            for dim in self.dimensions:
                dim.to_nc_container(nc)

            for var in self.variables:
                var.to_nc_container(nc, coordinates=coordinates, populate=populate)

            if self.groups is not None:
                for group in self.groups:
                    group.to_nc_container(nc, populate=populate)

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

    def create_example_file(
        self: HasDatasetAttributes,
        nc_filename: str,
        coordinates: Optional[str] = None,
        populate: bool = True,
    ) -> None:
        """
        Create an example file with the dataset's attributes, dimensions, variables, and groups.

        Args:
            nc_filename (str): The filename of the netCDF file to create.
            coordinates (Optional[str], optional): The name of the coordinate variable to use for the variables. Defaults to None.
            populate (bool, optional): Whether to populate the variables with data. Defaults to True.

        Yields:
            Generator[netCDF4.Dataset, None, None]: The created netCDF file.
        """
        with self._create_file(nc_filename, coordinates=coordinates, populate=populate) as nc:  # type: ignore # mixin difficulty
            pass

    @contextmanager
    def create_empty_file(
        self: HasDatasetAttributes, nc_filename: str
    ) -> Generator[netCDF4.Dataset, None, None]:
        """
        Context manager to create an empty netCDF file with the dataset's attributes, dimensions, variables, and groups.

        Args:
            nc_filename (str): The filename of the netCDF file to create.

        Yields:
            Generator[netCDF4.Dataset, None, None]: The created netCDF file.
        """
        with self._create_file(nc_filename, populate=False) as nc:  # type: ignore # mixin difficulty
            yield nc

    def to_cdl(self: HasDatasetAttributes, filename: str | None = None) -> str:
        """
        Convert the dataset to CDL.

        Returns:
            str: The CDL representation of the dataset.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            ncfile = os.path.join(tmpdir, f"{self.meta.short_name}.nc")

            with self.create_empty_file(ncfile) as nc:  # type: ignore # mixin difficulty
                pass

            with netCDF4.Dataset(ncfile, "r") as nc:
                cdl = nc.tocdl()

        if filename is not None:
            with open(filename, "w") as f:
                f.write(cdl)

        return cdl
