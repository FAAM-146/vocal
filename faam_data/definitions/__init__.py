from typing import Any

from faam_data.attributes.globals import GlobalAttributes
from faam_data.definitions import dimensions
from faam_data.attributes import (
    VariableAttributes, GroupAttributes, GlobalAttributes
)
from faam_data.templates import required_variable, required_globals
from ..variable import Variable

def make_1hz(var: Variable) -> Variable:
    """
    Take a Variable, and return a copy modified to represent a 1 Hz
    Variable
    """
    var = var.copy(deep=True)
    var.dimensions = [dimensions.Time]
    var.attributes.frequency = 1
    return var

def variable_attribute_factory(**kwargs: Any) -> VariableAttributes:
    """
    Return a VariableAttributes collection, containing all required 
    attributes, along with any specified optional attributes. Specified
    attributes may also be used to override defaults.
    """
    attributes = VariableAttributes.construct(**required_variable)
    for key, value in kwargs.items():
        setattr(attributes, key, value)
    return attributes

def group_attribute_factory(**kwargs: Any) -> GroupAttributes:
    """
    Return a GroupAttributes collection, containing all required 
    attributes, along with any specified optional attributes. Specified
    attributes may also be used to override defaults.
    """
    return GroupAttributes(**kwargs)

def global_attribute_factory(**kwargs: Any) -> GlobalAttributes:
    """
    Return a GlobalAttributes collection, containing all required 
    attributes, along with any specified optional attributes. Specified
    attributes may also be used to override defaults.
    """
    attributes = GlobalAttributes.construct(**required_globals)
    for key, value in kwargs.items():
        setattr(attributes, key, value)
    return attributes