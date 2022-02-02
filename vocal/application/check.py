"""Check a netCDF file against standard and product definitions."""

from argparse import Namespace
import importlib
import sys

from pydantic.error_wrappers import ValidationError

from vocal.core import register_defaults_module
from vocal.netcdf import NetCDFReader
from vocal.checking import ProductChecker
from pydantic import BaseModel

from . import parser_factory

LINE_LEN = 50

def print_line(len: int=50, token: str='-'):
    print(token * len)

def check_against_standard(model: BaseModel, filename: str) -> bool:
    print_line(LINE_LEN, '-')
    print(f'Checking {filename} against standard... ', end='')
    nc = NetCDFReader(filename)
    try:
        nc.to_model(model) # type: ignore
    except ValidationError as err:
        print('ERROR!')
        for e in err.errors():
            loc = ' --> ' + ' -> '.join([str(i) for i in e['loc']])
            print(f'{loc}: {e["msg"]}')
        print_line(LINE_LEN, '-')
        return False
    else:
        print('OK!')
        print_line(LINE_LEN, '-')
        return True

def check_against_specification(specification: str, filename: str) -> bool:
    pc = ProductChecker(specification)
    pc.check(filename)
    
    for check in pc.checks:
        print(f'{check.description}... ', end='')
        if check.passed:
            print('OK!')
        else:
            print('ERROR!')
            print(f' --> [{check.error.path}] {check.error.message}')

    print_line(LINE_LEN, '=')
    print(f'{len(pc.errors)} errors found.')
    print_line(LINE_LEN, '=')

    return pc.passing

def get_datamodel() -> BaseModel:
    
    Dataset = importlib.import_module('models').Dataset

    return Dataset

def register_defaults() -> None:
    try:
        defaults = importlib.import_module('defaults')
    except ModuleNotFoundError as e:
        raise RuntimeError('Unable to import project attributes') from e

    register_defaults_module(defaults)

def check_file(args: Namespace) -> None:
    sys.path.insert(0, args.project)

    register_defaults()
    ok1 = check_against_standard(model=get_datamodel(), filename=args.filename)

    if args.definition:
        ok2 = check_against_specification(args.definition, args.filename)
    else:
        ok2 = True

    if ok1 and ok2:
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