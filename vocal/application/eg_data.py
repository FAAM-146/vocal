"""Create an example data file from a definition."""

import importlib
from argparse import Namespace
import sys

from vocal.core import ProductDefinition, register_defaults_module

from . import parser_factory

def make_example_data(args: Namespace) -> None:
    project = args.project
    definition = args.definition
    output = args.output

    sys.path.insert(0, project)
    # from models import Dataset
    try:
        Dataset = importlib.import_module('models').Dataset
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project attributes') from e

    try:
        defaults = importlib.import_module('defaults')
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project attributes') from e

    register_defaults_module(defaults)

    product = ProductDefinition(definition, Dataset)
    product.create_example_file(output)

def main() -> None:

    parser = parser_factory(
        name='eg_data',
        description=__doc__
    )

    parser.add_argument(
        '-p', '--project', type=str, metavar='PROJECT',
        default='.', dest='project',
        help='The path of a vocal project to use. Defaults to current directory.'
    )

    parser.add_argument(
        '-d', '--definiton', type=str, metavar='DEFINITION',
        required=True, dest='definition',
        help='The product definition file to use for the example data.'
    )

    parser.add_argument(
        '-o', '--output', type=str, metavar='OUTPUT',
        dest='output', required=True,
        help='The output filename'
    )

    args = parser.parse_args(sys.argv[2:])

    make_example_data(args)