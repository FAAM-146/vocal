from __future__ import annotations
from typing import Callable, Protocol
import pydantic


class HasDatasetMeta(Protocol):
    file_pattern: str
    short_name: str


class HasGroupMeta(Protocol):
    name: str


class HasDatasetAttributes(Protocol):
    attributes: pydantic.BaseModel
    variables: list[HasVariableAttributes]
    dimensions: list[HasDimensionAttributes]
    groups: list[HasGroupAttributes]
    meta: HasDatasetMeta
    to_nc_container: Callable


class HasGroupAttributes(Protocol):
    attributes: pydantic.BaseModel
    variables: list[HasVariableAttributes]
    dimensions: list[HasDimensionAttributes]
    groups: list[HasGroupAttributes]
    meta: HasGroupMeta
    to_nc_container: Callable


class HasAttributeMeta(Protocol):
    name: str
    datatype: str


class HasVariableAttributes(Protocol):
    attributes: pydantic.BaseModel
    dimensions: list[str]
    meta: HasAttributeMeta
    to_nc_container: Callable


class HasDimensionAttributes(Protocol):
    name: str
    size: int | None
    to_nc_container: Callable
