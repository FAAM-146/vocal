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

def substitute_placeholders(cls, values):
        for key, value in values.items():
            
            if not isinstance(value, (str, list)):
                continue

            try:
                example = cls.schema()['properties'][key]['example']
            except KeyError:
                continue

            if 'derived' in value:
                values[key] = example
            
            if isinstance(value, list):
                replaced = []
                for i, list_val in enumerate(value):
                    if isinstance(list_val, str) and 'derived_from_file' in list_val:
                        replaced.append(example[i])
                    else:
                        replaced.append(list_val)

                values[key] = replaced
            
        return values