import numpy as np

__all__ = [
    'int8', 'int16', 'int32', 'int64',
    'uint8', 'uint16', 'uint32', 'uint64',
    'float16', 'float32', 'float64'
]


def numpy_type_factory(native_type: type, numpy_type: type, class_name: str) -> type:
    """
    Produce a pydantic type which validates a native type, and converts it to
    a numpy type. This is useful for ensuring numeric attributes are stored
    as the correct type in netCDF files.

    Args:
        native_type (type): The native type to validate.
        numpy_type (type): The numpy type to convert to.
        class_name (str): The name of the class to create.

    Returns:
        type: A pydantic type which validates native_type, and converts it to
            numpy_type.
    """
    def __get__validators__(cls):
        yield validate

    def validate(cls, v):
        if isinstance(v, numpy_type):
            return v
        
        if not isinstance(v, native_type):
            raise TypeError(f"Expected {native_type}, got {type(v)}")
        
        return numpy_type(v)
    
    return type(class_name, (native_type,), {
        '__get_validators__': classmethod(__get__validators__),
        'validate': classmethod(validate),
        'numpy_type': numpy_type
    })

int8 = numpy_type_factory(int, np.int8, "int8")
int16 = numpy_type_factory(int, np.int16, "int16")
int32 = numpy_type_factory(int, np.int32, "int32")
int64 = numpy_type_factory(int, np.int64, "int64")
uint8 = numpy_type_factory(int, np.uint8, "uint8")
uint16 = numpy_type_factory(int, np.uint16, "uint16")
uint32 = numpy_type_factory(int, np.uint32, "uint32")
uint64 = numpy_type_factory(int, np.uint64, "uint64")
float16 = numpy_type_factory(float, np.float16, "float16")
float32 = numpy_type_factory(float, np.float32, "float32")
float64 = numpy_type_factory(float, np.float64, "float64")