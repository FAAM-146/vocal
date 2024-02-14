"""Create versioned JSON product specifications."""

import glob
import os
import importlib.util
import sys

from argparse import Namespace

from . import parser_factory

from vocal.core import ProductCollection, register_defaults_module
from vocal.utils import import_project

def resolve_full_path(path: str) -> str:
    """
    Resolve a path to a full path if it is not already.

    Args:
        path: The path to resolve
    
    Returns:
        The resolved path
    """

    if not path.startswith('/'):
        path = os.path.join(os.getcwd(), path)
    return path


def release(args: Namespace) -> None:
    project = resolve_full_path(args.project)
    version = args.version
    output_dir = args.output_dir
    defs_dir = args.definitions

    if not os.path.isdir(project):
        raise ValueError(
            f'Project directory {project} does not exist'
             'please supply the full path to a vocal project directory'
        )

    try:
        module = import_project(project)
        print(dir(module))
        defaults = module.defaults
        
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project defaults') from e

    register_defaults_module(defaults)
    try:
        Dataset = module.models.Dataset
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project models') from e

    if not defs_dir:
        defs_dir = os.path.join(project, 'definitions')
    
    defs_dir = resolve_full_path(defs_dir)
    
    defs_glob = os.path.join(defs_dir, '*.yaml')

    collection = ProductCollection(model=Dataset, version=version)

    for defn in glob.glob(defs_glob):
        collection.add_product(defn)

    cwd = os.getcwd()

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    os.chdir(output_dir)
    try:
        collection.write_product_definitions()
    except Exception as e:
        raise RuntimeError('Failed to create versioned products') from e
    finally:
        os.chdir(cwd)
        

def main() -> None:
    parser = parser_factory(
        file=__file__,
        description='Create a versioned JSON product release.'
    )

    parser.add_argument(
        'project', type=str, metavar='PROJECT',
        help='The path of a vocal project for which to create vocabularies'
    )

    parser.add_argument(
        '-d', '--definitons', type=str, metavar='DEFINITION',
        dest='definitions',
        help=('The folder to look in for product definitions. '
              'Defaults to <project>/definitions')
    )

    parser.add_argument(
        '-v', '--version', type=str, required=True, metavar='VERSION', dest='version',
        help='The product version, e.g. 1.0'
    )

    parser.add_argument(
        '-o', '--output-dir', type=str, default='.', metavar='OUTPUT_DIR', dest='output_dir',
        help='The directory to write the versioned definitions to.'
    )

    args = parser.parse_args(sys.argv[2:])

    release(args)