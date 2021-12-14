from faam_data.definitions import dimensions
from faam_data.attributes import (
    VariableAttributes, GroupAttributes, GlobalAttributes
)
from faam_data.templates import required_variable, required_globals

def make_1hz(var):
    var = var.copy(deep=True)
    var.dimensions = [dimensions.Time]
    var.attributes.frequency = 1
    return var

def variable_attribute_factory(**kwargs):
    attributes = VariableAttributes.construct(**required_variable)
    for key, value in kwargs.items():
        setattr(attributes, key, value)
    return attributes

def group_attribute_factory(**kwargs):
    return GroupAttributes(**kwargs)

def global_attribute_factory(**kwargs):
    attributes = GroupAttributes.construct(**required_globals)
    for key, value in kwargs.items():
        setattr(attributes, key, value)
    return attributes