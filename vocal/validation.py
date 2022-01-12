import functools
from typing import Any, Callable, Collection
from pydantic import validator

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

# Shortcut defining a validator with allow_reuse set as True
re_validator = functools.partial(validator, allow_reuse=True)

def substitute_placeholders(cls, values: list) -> list:
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

