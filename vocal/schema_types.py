from typing import Union

import numpy as np

type_str = lambda typ: f'<{typ}>'

def derived_type(typ, optional=False):
    opt_str = ' optional' if optional else ''
    return f'<{typ}: derived_from_file{opt_str}>'

def derived_array(typ, optional=False):
    opt_str = ' optional' if optional else ''
    return f'<Array[{typ}]: derived_from_file{opt_str}>'

DerivedString = derived_type('str')
DerivedInteger32 = derived_type('int32')
DerivedInteger64 = derived_type('int64')
DerivedByte = derived_type('int8')
DerivedFloat32 = derived_type('float32')
DerivedFloat64 = derived_type('float64')

OptionalDerivedString = derived_type('str', optional=True)
OptionalDerivedInteger32 = derived_type('int32', optional=True)
OptionalDerivedInteger64 = derived_type('int64', optional=True)
OptionalDerivedByte = derived_type('int8', optional=True)
OptionalDerivedFloat32 = derived_type('float32', optional=True)
OptionalDerivedFloat64 = derived_type('float64', optional=True)

DerivedStringArray = derived_array('str')
DerivedInteger32Array = derived_array('int32')
DerivedInteger64Array = derived_array('int64')
DerivedByteArray = derived_array('int8')
DerivedFloat32Array = derived_array('float32')
DerivedFloat64Array = derived_array('float64')

OptionalDerivedStringArray = derived_array('str', optional=True)
OptionalDerivedInteger32Array = derived_array('int32', optional=True)
OptionalDerivedInteger64Array = derived_array('int64', optional=True)
OptionalDerivedByteArray = derived_array('int8', optional=True)
OptionalDerivedFloat32Array = derived_array('float32', optional=True)
OptionalDerivedFloat64Array = derived_array('float64', optional=True)

Numeric = Union[float, int]

Byte = type_str('int8')
Integer8 = type_str('int8')
Integer16 = type_str('int16')
Integer32 = type_str('int32')
Integer64 = type_str('int64')
Float32 = type_str('float32')
Float64 = type_str('float64')
String = type_str('str')

np_invert = {
    np.dtype('float32'): Float32,
    np.dtype('float64'): Float64,
    np.dtype('int8'): Integer8,
    np.dtype('int16'): Integer16,
    np.dtype('int32'): Integer32,
    np.dtype('int64'): Integer64,
    np.dtype('float32'): Float32,
    np.dtype('float64'): Float64,
    np.dtype('str'): String,
    str: String,
    float: Float32,
    np.float32: Float32,
    np.int64: Integer64,
    np.int32: Integer32,
    np.int8: Integer8,
    np.byte: Byte,
    list: list
}

def type_from_spec(spec):
    spec = spec.replace('<', '').replace('>', '')
    try:
        return getattr(np, spec)
    except AttributeError:
        pass

    if spec == 'str':
        return str
    
    if spec == 'list':
        return list