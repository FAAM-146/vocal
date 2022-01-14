"""Create versioned JSON vocabularies for a vocal project"""

import glob
import os
import importlib
import sys

from argparse import Namespace

from . import parser_factory

from vocal.core import DataModel, register_defaults_module, ProductCollection

def create_vocabs(args: Namespace) -> None:
    project = args.project
    version = args.version
    output_dir = args.output_dir

    sys.path.insert(0, project)
    # Use importlib to prevent pylance moaning...
    try:
        attributes = importlib.import_module('attributes')
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project attributes') from e

    try:
        defaults = importlib.import_module('defaults')
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project defaults') from e

    register_defaults_module(defaults)
    dm = DataModel(attributes)

    defs_dir = os.path.join(project, 'definitions')
    defs_glob = os.path.join(defs_dir, '*.yaml')

    collection = ProductCollection(model=dm, version=version)

    for defn in glob.glob(defs_glob):
        collection.add_product(defn)

    cwd = os.getcwd()

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    os.chdir(output_dir)
    try:
        collection.write_vocabularies()
    except Exception as e:
        raise RuntimeError('Failed to create vocabularies') from e
    finally:
        os.chdir(cwd)
        

def main() -> None:
    parser = parser_factory(
        name='create_vocabs',
        description='Create versioned JSON vocabularies for a vocal project'
    )

    parser.add_argument(
        'project', type=str, metavar='PROJECT',
        help='The path of a vocal project for which to create vocabularies'
    )

    parser.add_argument(
        '-v', '--version', type=str, required=True, metavar='VERSION', dest='version',
        help='The vocabulary version, e.g. 1.0'
    )

    parser.add_argument(
        '-o', '--output-dir', type=str, default='.', metavar='OUTPUT_DIR', dest='output_dir',
        help='The directory to write the vocabularies to.'
    )


    args = parser.parse_args(sys.argv[2:])

    create_vocabs(args)