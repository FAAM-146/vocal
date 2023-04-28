import functools
import random

from string import ascii_lowercase, ascii_uppercase
from typing import Any, Callable, Collection
from pydantic import validator, root_validator

def _randomize_object_name(obj: Any) -> Any:
    """
    Randomize the name of an object (__name__), to work around a
    bug-or-odd-feature in pydantic

    Args:
        obj: the object to rename

    Returns:
        obj with a random __name__
    """
    _random_str = ''.join(random.sample(ascii_lowercase + ascii_uppercase, 12))
    obj.__name__ = _random_str
    return obj

def default_value_factory(default: Any) -> Callable:
    """
    Provides a validator which ensures an attribute takes a given default 
    value
    """
    def _validator(cls, value):
        if value != default:
            raise ValueError(f'Text is incorrect. Should read: "{default}"')
        return value
    return _validator

def is_in_factory(collection: Collection) -> Callable:
    """
    Provides a validator which ensures an attribute takes a value in a
    given collection
    """
    def _validator(cls, value):
        if value not in collection:
            raise ValueError(f'Value should be in {collection}')
        return value
    return _validator

def variable_exists_factory(variable_name: str) -> Callable:
    """
    Provides a validator which ensures a variable exists in a given
    group
    """
    def _validator(cls, values):
        variables = values.get('variables', [])
        name = values.get('meta').name
        if variables is None:
            raise ValueError(f'Variable \'{variable_name}\' not found in {name}')

        for var in variables:
            if var.meta.name == variable_name:
                return values
        raise ValueError(f'Variable \'{variable_name}\' not found in {name}')

    return _randomize_object_name(_validator)

def group_exists_factory(group_name: str) -> Callable:
    """
    Provides a validator which ensures a variable exists in a given
    group
    """
    def _validator(cls, values):
        groups = values.get('groups', [])
        name = values.get('meta').name
        if groups is None:
            raise ValueError(f'Group \'{group_name}\' not found in {name}')

        for group in groups:
            if group.meta.name == group_name:
                return values
        raise ValueError(f'Group \'{group_name}\' not found in {name}')

    return _randomize_object_name(_validator)

def dimension_exists_factory(dimension_name: str) -> Callable:
    """
    Provides a validator which ensures a variable exists in a given
    group
    """
    def _validator(cls, values):
        dimensions = values.get('dimensions', [])
        name = values.get('meta').name
        if dimensions is None:
            raise ValueError(f'Dimension \'{dimension_name}\' not found in {name}')

        for dim in dimensions:
            if dim.name == dimension_name:
                return values
        raise ValueError(f'Dimension \'{dimension_name}\' not found in {name}')

    return _randomize_object_name(_validator)


# Shortcut defining a validator with allow_reuse set as True
re_validator = functools.partial(validator, allow_reuse=True)
re_root_validator = functools.partial(root_validator, allow_reuse=True)

def substitute_placeholders(cls, values: dict) -> dict:
    """
    A root validator, which should be called with pre=True, which turns
    attributes with placeholders (e.g. attr: <str: derived_from_file>)
    into valid values, by substituting them with the example from the attribute
    definition.
    """
    DERIVED = 'derived_from_file'

    for key, value in values.items():
        
        if not isinstance(value, (str, list)):
            continue

        try:
            example = cls.schema()['properties'][key]['example']
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

