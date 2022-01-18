from typing import NewType, Union

import numpy as np


derived_str = lambda typ: f'<{typ}: derived_from_file>'
DerivedType = NewType('DerivedType', str)
DerivedString = DerivedType(derived_str('str'))
DerivedInteger32 = DerivedType(derived_str('int32'))
DerivedInteger64 = DerivedType(derived_str('int64'))
DerivedByte = DerivedType(derived_str('byte'))
DerivedFloat32 = DerivedType(derived_str('float32'))
DerivedFloat64 = DerivedType(derived_str('float64'))
Numeric = Union[float, int]

type_str = lambda typ: f'<{typ}>'
InfoType = NewType('InfoType', str)
Byte = InfoType(type_str('byte'))
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
    float: Float32
}
