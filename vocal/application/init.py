"""Initialise a vocal project."""

from argparse import ArgumentParser, Namespace
import os
import sys

from pydantic.types import NonNegativeFloat

from . import parser_factory

ATTRIBUTES_TEMPLATE = """
from pydantic import Field
from vocal.attributes import AttributesSet

class {attr_type}Attributes(AttributesSet):
    class Config:
        # Configuration options here
        title = 'My {attr_type} attributes'

    # Add your attributes here, e.g.
    #
    # my_attribute: str = Field(
    #   description='A description of my attribute',
    #   example='my_attribute_value'
    # )
"""

ATTRIBUTES_INIT = """
from .global_attributes import GlobalAttributes
from .variable_attributes import VariableAttributes
from .group_attributes import GroupAttributes
"""

MODELS_INIT = """
from .dataset import Dataset, DatasetMeta
from .variable import Variable, VariableMeta
from .group import Group, GroupMeta
from .dimension import dimension
"""

DEFAULTS = """
from vocal.schema_types import *

# Add your attribute default values here:

default_global_attrs = {}
default_group_attrs = {}
default_variable_attrs = {}
"""

DATASET_CODE = """
from __future__ import annotations
from typing import Optional
import netCDF4 # type: ignore

from pydantic import BaseModel, Field

from .dimension import Dimension
from .attributes import AttributesSet
from .group import Group
from .variable import Variable

class DatasetMeta(BaseModel):
    file_pattern: str = Field(description='Canonical filename pattern for this dataset')


class Dataset(BaseModel):
    class Config:
        title = 'Dataset Schema'

    meta: DatasetMeta
    attributes: AttributesSet
    dimensions: list[Dimension]
    groups: Optional[list[Group]]
    variables: list[Variable]
"""

GROUP_CODE = """
from __future__ import annotations
from typing import Optional

from pydantic import BaseModel

from .dimension import Dimension
from .variable import Variable
from .attributes import AttributesSet

class GroupMeta(BaseModel):
    class Config:
        title = 'Group Metadata'

    name: str

class Group(BaseModel):
    class Config:
        title = 'Group Schema'

    meta: GroupMeta
    attributes: AttributesSet
    dimensions: Optional[list[Dimension]]
    groups: Optional[list[Group]]
    variables: list[Variable]
"""

VARIABLE_CODE = """
import netCDF4 # type: ignore
import numpy as np
import numpy.typing
from pydantic import BaseModel, Field
from typing import List
from .training import variable_data_hooks, VariableTrainingData
from .attributes import AttributesSet


class VariableMeta(BaseModel):
    datatype: str = Field(description='The type of the data')
    name: str


class Variable(BaseModel):
    meta: VariableMeta
    dimensions: List[str]
    attributes: AttributesSet

    @property
    def np_type(self) -> numpy.typing.DTypeLike:
        dtypes = {
            '<int32>': np.int32,
            '<int64>': np.int64,
            '<int8>': np.int8,
            '<byte>': np.byte,
            '<float32>': np.float32,
            '<float64>': np.float64
        }

        return dtypes[self.meta.datatype]
"""

DIMENSION_CODE = """
from pydantic import BaseModel
from typing import Union


class Dimension(BaseModel):
    name: str
    size: Union[int, None]
"""

def make_definitions_dir(folder: str) -> None:
    def_dir = os.path.join(folder, 'definitions')
    os.mkdir(def_dir)

def make_defaults_module(folder: str) -> None:
    filename = os.path.join(folder, 'defaults.py')
    with open(filename, 'w') as f:
        f.write(DEFAULTS)

def make_attributes_init(folder: str) -> None:
    filename = os.path.join(folder, '__init__.py')
    with open(filename, 'w') as f:
        f.write(ATTRIBUTES_INIT)

def make_attributes_file(folder: str, attr_type: str) -> None:
    filename = os.path.join(folder, f'{attr_type.lower()}_attributes.py')
    with open(filename, 'w') as f:
        f.write(ATTRIBUTES_TEMPLATE.format(attr_type=attr_type))

def make_attributes_module(parent_folder: str) -> None:
    folder = os.path.join(parent_folder, 'attributes')
    os.mkdir(folder)
    for attr_type in ('Global', 'Group', 'Variable'):
        make_attributes_file(folder, attr_type)
    make_attributes_init(folder)

def make_models_init(folder: str) -> None:
    filename = os.path.join(folder, '__init__.py')
    with open(filename, 'w') as f:
        f.write(MODELS_INIT)

def make_model_file(folder: str, model: str) -> None:
    filename = os.path.join(folder, f'{model.lower()}.py')
    text = globals()[f'{model}_CODE']
    with open(filename, 'w') as f:
        f.write(text)

def make_models_module(parent_folder: str) -> None:
    folder = os.path.join(parent_folder, 'models')
    os.mkdir(folder)
    for model in ('DIMENSION', 'VARIABLE', 'GROUP', 'DATASET'):
        make_model_file(folder, model)
    make_models_init(folder)

def init_project(args: Namespace) -> None:
    folder = args.directory[0]

    try:
        os.mkdir(folder)
    except FileExistsError:
        print(f'Initializing into existing folder: {folder}')

    make_attributes_module(folder)
    make_defaults_module(folder)
    make_definitions_dir(folder)
    make_models_module(folder)


def main() -> None:
    parser = parser_factory(
        name='init',
        description='Initialise a vocal project'
    )

    parser.add_argument(
        '-d', type=str, nargs=1, default='.',
        metavar='DIRECTORY', dest='directory',
        help='The directory in which to create the project. Defaults to cwd.'
    )

    args = parser.parse_args(sys.argv[2:])

    init_project(args)
