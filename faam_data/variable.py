import netCDF4
import numpy as np
from pydantic import BaseModel, Field
from typing import List
from .training import variable_data_hooks, VariableTrainingData
from .attributes import VariableAttributes
from .dimension import Dimension

class VariableMeta(BaseModel):
    datatype: str = Field(description='The type of the data')
    name: str


class Variable(BaseModel):
    meta: VariableMeta
    dimensions: List[Dimension]
    attributes: VariableAttributes

    @property
    def np_type(self) -> np.dtype:
        dtypes = {
            '<int32>': np.int32,
            '<int64>': np.int64,
            '<int8>': np.int8,
            '<byte>': np.byte,
            '<float32>': np.float32,
            '<float64>': np.float64
        }

        return dtypes[self.meta.datatype]

    def to_nc_container(self, nc: netCDF4.Dataset) -> netCDF4.Variable:
        print(f'creating variable {self.meta.name}')
        var = nc.createVariable(
            self.meta.name,
            self.np_type,
            [i.name for i in self.dimensions],
            fill_value=self.attributes._FillValue
        )

        VariableTrainingData(var, self.attributes).populate()

        for attr, value in self.attributes:
            try:
                value = variable_data_hooks[attr](var)
            except KeyError:
                pass

            if value is None:
                continue

            if attr == '_FillValue':
                continue

            setattr(var, attr, value)

        return var