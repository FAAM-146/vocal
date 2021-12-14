
from faam_data.variable import Variable, VariableMeta
from faam_data.schema_types import DerivedFloat32, DerivedString, Float32
from faam_data.definitions.dimensions import Time, sps32
from faam_data.definitions import variable_attribute_factory

variables = [
    Variable(
        meta=VariableMeta(
            name='TAT_DI_R',
            datatype=Float32,
        ),
        dimensions=[Time, sps32],
        attributes=variable_attribute_factory(
            long_name=DerivedString,
            standard_name='air_temperature',
            units='K',
            frequency=32,
            coverage_content_type='physicalMeasurement',
            actual_range=[DerivedFloat32, DerivedFloat32],
        )
    ),

    Variable(
        meta=VariableMeta(
            name='TAT_ND_R',
            datatype=Float32,
        ),
        dimensions=[Time, sps32],
        attributes=variable_attribute_factory(
            long_name=DerivedString,
            standard_name='air_temperature',
            units='K',
            frequency=32,
            coverage_content_type='physicalMeasurement',
            actual_range=[DerivedFloat32, DerivedFloat32]
        )
    )
]