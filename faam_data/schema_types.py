from typing import NewType, Union


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
Integer32 = InfoType(type_str('int32'))
Integer64 = InfoType(type_str('int64'))
Float32 = InfoType(type_str('float32'))
Float64 = InfoType(type_str('float64'))
String = InfoType(type_str('string'))
