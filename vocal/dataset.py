from __future__ import annotations
import netCDF4 # type: ignore

from .training import global_data_hooks


class DatasetNetCDFMixin:

    def create_example_file(self, nc_filename: str) -> None:
        
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
                    setattr(nc, attr, value)
                except TypeError:
                    setattr(nc, attr, str(value))