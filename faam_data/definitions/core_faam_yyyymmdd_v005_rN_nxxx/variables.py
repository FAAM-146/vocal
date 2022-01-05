
from faam_data import attributes
from faam_data.variable import Variable, VariableMeta
from faam_data.schema_types import DerivedFloat32, DerivedString, Float32
from faam_data.definitions.dimensions import Time, sps32
from faam_data.definitions import variable_attribute_factory

variables = [
    Variable(
        meta=VariableMeta(
            name='Time',
            datatype=Float32
        ),
        dimensions=[Time],
        attributes=variable_attribute_factory(
            long_name='Time',
            units='seconds since 1970-01-01T00:00:00Z',
            standard_name='time',
            axis='T',
            coverage_content_type='coordinate',
            frequency=1
        )
    ),

    Variable(
        meta=VariableMeta(
            name='LAT_GIN',
            datatype=Float32
        ),
        dimensions=[Time, sps32],
        attributes=variable_attribute_factory(
            long_name='Latitude from GIN',
            units='degree_north',
            standard_name='latitude',
            axis='Y',
            frequency=32,
            coverage_content_type='coordinate'
        )
    ),

    Variable(
        meta=VariableMeta(
            name='LON_GIN',
            datatype=Float32
        ),
        dimensions=[Time, sps32],
        attributes=variable_attribute_factory(
            long_name='Longitude from GIN',
            units='degree_east',
            standard_name='longitude',
            axis='X',
            frequency=32,
            coverage_content_type='coordinate'
        )
    ),

    Variable(
        meta=VariableMeta(
            name='ALT_GIN',
            datatype=Float32
        ),
        dimensions=[Time, sps32],
        attributes=variable_attribute_factory(
            long_name='Altitude from GIN',
            units='m',
            standard_name='latitude',
            axis='Z',
            frequency=32,
            coverage_content_type='coordinate'
        )
    ),

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