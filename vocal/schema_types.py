import sys

from typing import NewType, Union

import numpy as np

def derived_str(typ, optional=False):
    opt_str = ' optional' if optional else ''
    return f'<{typ}: derived_from_file{opt_str}>'

DerivedType = NewType('DerivedType', str)
DerivedString = DerivedType(derived_str('str'))
DerivedInteger32 = DerivedType(derived_str('int32'))
DerivedInteger64 = DerivedType(derived_str('int64'))
DerivedByte = DerivedType(derived_str('int8'))
DerivedFloat32 = DerivedType(derived_str('float32'))
DerivedFloat64 = DerivedType(derived_str('float64'))

OptionalDerivedString = DerivedType(derived_str('str', optional=True))
OptionalDerivedInteger32 = DerivedType(derived_str('int32', optional=True))
OptionalDerivedInteger64 = DerivedType(derived_str('int64', optional=True))
OptionalDerivedByte = DerivedType(derived_str('int8', optional=True))
OptionalDerivedFloat32 = DerivedType(derived_str('float32', optional=True))
OptionalDerivedFloat64 = DerivedType(derived_str('float64', optional=True))

Numeric = Union[float, int]

type_str = lambda typ: f'<{typ}>'
InfoType = NewType('InfoType', str)
Byte = InfoType(type_str('int8'))
Integer8 = InfoType(type_str('int8'))
Integer16 = InfoType(type_str('int16'))
Integer32 = InfoType(type_str('int32'))
Integer64 = InfoType(type_str('int64'))
Float32 = InfoType(type_str('float32'))
Float64 = InfoType(type_str('float64'))
String = InfoType(type_str('str'))

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
