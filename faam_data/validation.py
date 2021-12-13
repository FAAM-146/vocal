import functools
from pydantic import validator

def default_value_factory(default):
    def _validator(cls, value):
        if value != default:
            raise ValueError(f'Text is incorrect. Should read: "{default}"')
        return value
    return _validator

def is_in_factory(collection):
    def _validator(cls, value):
        if value not in collection:
            raise ValueError(f'Value should be in {collection}')
        return value
    return _validator


re_validator = functools.partial(validator, allow_reuse=True)