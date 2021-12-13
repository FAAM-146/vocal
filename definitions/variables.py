from faam_data.attributes import VariableAttributes
from faam_data.constants import COVERAGE_CONTENT_TYPES
from faam_data.variable import Variable, VariableMeta
from faam_data.attributes import VariableAttributes
from faam_data.templates import required_variable
from faam_data.schema_types import DerivedFloat32, DerivedString, Float32
from dimensions import *

def make_1hz(var):
    var = var.copy(deep=True)
    var.meta.dimensions = [Time]
    var.attributes.frequency = 1
    return var

def attribute_factory(**kwargs):
    attributes = VariableAttributes.construct(**required_variable)
    for key, value in kwargs.items():
        setattr(attributes, key, value)
    return attributes

TAT_DI_R = Variable(
    meta=VariableMeta(
        name='TAT_DI_R',
        datatype=Float32,
        dimensions=[Time, sps32]
    ),
    attributes=attribute_factory(
        long_name=DerivedString,
        standard_name='air_temperature',
        units='K',
        frequency=32,
        coverage_content_type='physicalMeasurement',
        actual_range=[DerivedFloat32, DerivedFloat32]
    )
)

TAT_DI_R_1HZ = make_1hz(TAT_DI_R)

import json
print(json.dumps(TAT_DI_R.dict(exclude_unset=True), indent=2))