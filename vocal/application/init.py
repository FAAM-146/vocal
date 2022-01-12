from argparse import ArgumentParser, Namespace
import os
import sys

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

DEFAULTS = """
from vocal.schema_types import *

# Add your attribute default values here:

default_global_attrs = {}
default_group_attrs = {}
default_variable_attrs = {}
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

def init_project(args: Namespace) -> None:
    folder = args.directory[0]

    try:
        os.mkdir(folder)
    except FileExistsError:
        print(f'Initializing into existing folder: {folder}')

    make_attributes_module(folder)
    make_defaults_module(folder)
    make_definitions_dir(folder)


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
