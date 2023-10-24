from pydantic import Field as _Field

pydantic_v2_args = [
    'default',
    'default_factory',
    'alias',
    'alias_priority',
    'validation_alias',
    'serialization_alias',
    'title',
    'description',
    'examples',
    'exclude',
    'discriminator',
    'json_schema_extra',
    'frozen',
    'validate_default',
    'repr',
    'init_var',
    'kw_only',
    'strict',
    'gt',
    'ge',
    'lt',
    'le',
    'multiple_of',
    'min_length',
    'max_length',
    'pattern',
    'allow_inf_nan',
    'max_digits',
    'decimal_places',
    'union_mode'
]


def Field(*args, **kwargs):
    """
    This is a wrapper around pydantic's Field that allows for extra arguments
    to be passed to the schema directly, rather than using the `json_schema_extra`
    argument. This is the way things were done in pydantic v1. Here, we allow
    this behavior to continue for backwards compatibility, but pass the extra
    arguments to the `json_schema_extra` argument to avoid the deprecation
    warning.
    """
    json_schema_extra = kwargs.pop('json_schema_extra', {})
    new_kwargs = {}
    for key in kwargs:
        if key not in pydantic_v2_args:
            json_schema_extra[key] = kwargs[key]
        else:
            new_kwargs[key] = kwargs[key]
        

    return _Field(*args, json_schema_extra=json_schema_extra, **new_kwargs)