from typing import Any

import copy
import pydantic
import yaml

from faam_data.attributes.globals import GlobalAttributes
from faam_data.definitions import dimensions
from faam_data.attributes import (
    VariableAttributes, GroupAttributes, GlobalAttributes
)
from faam_data.templates import required_variable, required_globals
from ..variable import Variable
from ..dataset import Dataset

def make_1hz(var: Variable) -> Variable:
    """
    Take a Variable, and return a copy modified to represent a 1 Hz
    Variable
    """
    var = var.copy(deep=True)
    var.dimensions = ['Time']
    var.attributes.frequency = 1
    return var

def variable_attribute_factory(**kwargs: Any) -> VariableAttributes:
    """
    Return a VariableAttributes collection, containing all required 
    attributes, along with any specified optional attributes. Specified
    attributes may also be used to override defaults.
    """
    attributes = VariableAttributes.construct(**required_variable) # type: ignore
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
    attributes = GlobalAttributes.construct(**required_globals) # type: ignore
    for key, value in kwargs.items():
        setattr(attributes, key, value)
    return attributes

def dataset_from_partial_yaml(yamlfile: str) -> pydantic.BaseModel:
    def parse_definition(defn: dict, ctype: str='dataset') -> dict:    
        for var in defn['variables']:
            
            _temp = copy.deepcopy(required_variable)
            _temp.update(var['attributes'])
            var['attributes'] = _temp

        try:
            for g in defn['groups']:
                parse_definition(g, ctype='group')
        except KeyError:
            pass

        if ctype == 'dataset':
            _temp = copy.deepcopy(required_globals)
            _temp.update(defn['attributes'])
            defn['attributes'] = _temp

        return defn
        
    with open(yamlfile, 'r') as f:
        y = yaml.load(f, Loader=yaml.Loader)
        dataset = Dataset.construct(**parse_definition(y['Dataset']))

    return dataset