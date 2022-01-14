"""Check a netCDF file against standard and product definitions."""

from argparse import Namespace
import importlib
import sys

from pydantic.error_wrappers import ValidationError

from vocal.core import DataModel, register_defaults_module
from vocal.netcdf import NetCDFReader

from . import parser_factory

def check_against_standard(model: DataModel, filename: str) -> bool:
    print(f'Checking {filename} against standard... ', end='')
    nc = NetCDFReader(filename)
    try:
        nc.to_model(model.model) # type: ignore
    except ValidationError as err:
        print('FAIL!')
        for e in err.errors():
            loc = ' -> '.join([str(i) for i in e['loc']])
            print(f'{loc}: {e["msg"]}')
        return False
    else:
        print('OK!')
        return True

def get_datamodel() -> DataModel:
    
    try:
        attributes = importlib.import_module('attributes')
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project attributes') from e

    return DataModel(attributes)

def register_defaults() -> None:
    try:
        defaults = importlib.import_module('defaults')
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project attributes') from e

    register_defaults_module(defaults)

def check_file(args: Namespace) -> None:
    sys.path.insert(0, args.project)

    register_defaults()
    ok = check_against_standard(model=get_datamodel(), filename=args.filename)

    if ok:
        sys.exit(0)
    else:
        sys.exit(1)

def main() -> None:
    parser = parser_factory(
        name='check',
        description='Check a file against standard and/or product definition'
    )

    parser.add_argument(
        'filename', type=str, metavar='FILE',
        help='The netCDF file to check'
    )

    parser.add_argument(
        '-p' , '--project', dest='project', type=str, metavar='PROJECT',
        help='Path to the vocal project, defaults to current directory.', default='.'
    )

    parser.add_argument(
        '-d',  '--definition', dest='definition', type=str, metavar='DEFINITION',
        default=None,
        help='Product definition to test against'
    )

    args = parser.parse_args(sys.argv[2:])

    check_file(args)