from typing import Any, Optional, Protocol
import datetime

import netCDF4 # type: ignore
import numpy as np
import numpy.typing
import pydantic

from ...training import variable_data_hooks, VariableTrainingData

class HasAttributeMeta(Protocol):
    name: str
    datatype: str

class HasVariableAttributes(Protocol):
    attributes: pydantic.BaseModel
    dimensions: list[str]
    meta: HasAttributeMeta
    np_type: numpy.typing.DTypeLike

class VariableNetCDFMixin:

    @property
    def np_type(self: HasVariableAttributes) -> numpy.typing.DTypeLike:
        dtypes = {
            '<int32>': np.int32,
            '<int64>': np.int64,
            '<int16>': np.int16,
            '<int8>': np.int8,
            '<uint32>': np.uint32,
            '<uint64>': np.uint64,
            '<uint16>': np.uint16,
            '<uint8>': np.uint8,
            '<byte>': np.byte,
            '<float32>': np.float32,
            '<float64>': np.float64
        }

        return dtypes[self.meta.datatype]

    def to_nc_container(
        self: HasVariableAttributes, nc: netCDF4.Dataset, coordinates: Optional[str]=None
    ) -> netCDF4.Variable:
        print(f'creating variable {self.meta.name}')

        # Seems to be some inconsistent behaviour with the alias, try both
        # before failing
        try:
            fv = self.attributes.FillValue # type: ignore
        except AttributeError:
            try:
                fv = self.attributes._FillValue # type: ignore
            except AttributeError:
                fv = None

        var = nc.createVariable(
            self.meta.name,
            self.np_type,
            self.dimensions,
            fill_value=fv # type: ignore
        )

        VariableTrainingData(var, self.attributes).populate()

        for attr, value in self.attributes:

            # Deal with the case where non-local coordinates are given.
            # This is such a kludge.
            if coordinates is not None:
                if attr == 'coordinates' and self.attributes.dict()['coordinates'] is not None:
                    setattr(var, attr, coordinates)
                    continue
            try:
                value = variable_data_hooks[attr](var, self.attributes)
            except KeyError:
                pass

            if value is None:
                continue

            if attr in ('_FillValue', 'FillValue'):
                continue

            if isinstance(value, datetime.date):
                value = value.strftime('%Y-%m-%d')

            if isinstance(value, datetime.datetime):
                value = value.strftime('%Y-%m-%dT%H:%M:%SZ')

            setattr(var, attr, value)

        return var