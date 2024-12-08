import functools
import random

from string import ascii_lowercase, ascii_uppercase
from typing import Any, Callable, Collection
from pydantic import model_validator, field_validator


def _randomize_object_name(obj: Any) -> Any:
    """
    Randomize the name of an object (__name__), to work around a
    bug-or-odd-feature in pydantic

    Args:
        obj: the object to rename

    Returns:
        obj with a random __name__
    """
    _random_str = "".join(random.sample(ascii_lowercase + ascii_uppercase, 12))
    obj.__name__ = _random_str
    return obj


def default_value(default: Any) -> Callable:
    """
    Provides a validator which ensures an attribute takes a given default
    value
    """

    def _validator(cls, value):
        if value != default:
            raise ValueError(f'text is incorrect. Got: "{value}", expected "{default}"')
        return value

    return _randomize_object_name(_validator)


def is_in(collection: Collection) -> Callable:
    """
    Provides a validator which ensures an attribute takes a value in a
    given collection
    """

    def _validator(cls, value):
        if value not in collection:
            raise ValueError(f"Value should be in {collection}")
        return value

    return _randomize_object_name(_validator)


def variable_exists(variable_name: str) -> Callable:
    """
    Provides a validator which ensures a variable exists in a given
    group
    """

    def _validator(cls, values):
        try:
            variables = values.variables
        except Exception:
            variables = []
        name = values.meta.name
        if variables is None:
            raise ValueError(f"Variable '{variable_name}' not found in {name}")

        for var in variables:
            if var.meta.name == variable_name:
                return values
        raise ValueError(f"Variable '{variable_name}' not found in {name}")

    return _randomize_object_name(_validator)


def variable_has_types(variable_name: str, allowed_types: list[str]) -> Callable:
    def _validator(cls, values):
        variables = values.variables
        if variables is None:
            return values
        for var in variables:
            var_name = var.meta.name
            var_type = var.meta.datatype
            if var_name != variable_name:
                continue
            if var_type not in allowed_types:
                raise ValueError(
                    f'Expected datatype of variable "{variable_name}" to be '
                    f'one of [{",".join(allowed_types)}], got {var_type}'
                )
        return values

    return _randomize_object_name(_validator)


def variable_has_dimensions(variable_name: str, dimensions: list[str]) -> Callable:
    def _validator(cls, values):
        variables = values.variables
        if variables is None:
            return values
        for var in variables:
            if var.meta.name != variable_name:
                continue

            var_dims = var.dimensions
            for dim in dimensions:
                if dim not in var_dims:
                    raise ValueError(
                        f'Expected variable "{variable_name}" to have dimension "{dim}"'
                    )

            for dim in var_dims:
                if dim not in dimensions:
                    raise ValueError(
                        f'Variable "{variable_name}" has unexpected dimension ' f"{dim}"
                    )
        return values

    return _randomize_object_name(_validator)


def group_exists(group_name: str) -> Callable:
    """
    Provides a validator which ensures a variable exists in a given
    group
    """

    def _validator(cls, values):
        try:
            groups = values.groups
        except Exception:
            groups = []
        name = values.meta.name
        if groups is None:
            raise ValueError(f"Group '{group_name}' not found in {name}")

        for group in groups:
            if group.meta.name == group_name:
                return values
        raise ValueError(f"Group '{group_name}' not found in {name}")

    return _randomize_object_name(_validator)


def dimension_exists(dimension_name: str) -> Callable:
    """
    Provides a validator which ensures a variable exists in a given
    group
    """

    def _validator(cls, values):
        dimensions = values.dimensions
        name = values.meta.name
        if dimensions is None:
            raise ValueError(f"Dimension '{dimension_name}' not found in {name}")

        for dim in dimensions:
            if dim.name == dimension_name:
                return values
        raise ValueError(f"Dimension '{dimension_name}' not found in {name}")

    return _randomize_object_name(_validator)


# These were more customised for pydantic v1. They're mostly passthroughs now.
substitutor = model_validator(mode="before")
validator = model_validator(mode="after")


def substitute_placeholders(cls, values: dict) -> dict:
    """
    A root validator, which should be called with pre=True, which turns
    attributes with placeholders (e.g. attr: <str: derived_from_file>)
    into valid values, by substituting them with the example from the attribute
    definition.
    """
    DERIVED = "derived_from_file"

    for key, value in values.items():

        if not isinstance(value, (str, list)):
            continue

        try:
            example = cls.model_json_schema()["properties"][key]["example"]
        except KeyError:
            continue

        if DERIVED in value:
            values[key] = example

        # Traverse any lists and replace values
        if isinstance(value, list):
            replaced = []
            for i, list_val in enumerate(value):
                if isinstance(list_val, str) and DERIVED in list_val:
                    replaced.append(example[i])
                else:
                    replaced.append(list_val)

            values[key] = replaced

    return values
