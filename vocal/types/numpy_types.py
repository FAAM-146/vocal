from typing import Annotated

from pydantic import AfterValidator
import numpy as np

__all__ = [
    'int8', 'int16', 'int32', 'int64',
    'uint8', 'uint16', 'uint32', 'uint64',
    'float16', 'float32', 'float64'
]

int8 = Annotated[int, AfterValidator(np.int8)]
int16 = Annotated[int, AfterValidator(np.int16)]
int32 = Annotated[int, AfterValidator(np.int32)]
int64 = Annotated[int, AfterValidator(np.int64)]

uint8 = Annotated[int, AfterValidator(np.uint8)]
uint16 = Annotated[int, AfterValidator(np.uint16)]
uint32 = Annotated[int, AfterValidator(np.uint32)]
uint64 = Annotated[int, AfterValidator(np.uint64)]

float16 = Annotated[float, AfterValidator(np.float16)]
float32 = Annotated[float, AfterValidator(np.float32)]
float64 = Annotated[float, AfterValidator(np.float64)]