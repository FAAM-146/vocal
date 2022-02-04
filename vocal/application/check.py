"""Check a netCDF file against standard and product definitions."""

from argparse import Namespace
from dataclasses import dataclass
import importlib
import sys

from pydantic.error_wrappers import ValidationError

from vocal.core import register_defaults_module
from vocal.netcdf import NetCDFReader
from vocal.checking import ProductChecker
from pydantic import BaseModel

from . import parser_factory

LINE_LEN = 50


@dataclass
class Printer:
    quiet: bool = False
    errors_only: bool = False

    def print_line(self, len: int=50, token: str='-'):
        if self.quiet or self.errors_only:
            return
        print(token * len)

    def print_line_err(self, len: int=50, token: str='-'):
        if self.quiet:
            return
        print(token * len)

    def print(self, *args, **kwargs):
        if self.quiet or self.errors_only:
            return

        print(*args, **kwargs)
        
    def print_err(self, *args, **kwargs):
        if self.quiet:
            return

        print(*args, **kwargs)

p = Printer()
    

def check_against_standard(model: BaseModel, filename: str) -> bool:
    p.print_line(LINE_LEN, '-')
    p.print(f'Checking {filename} against standard... ', end='')
    nc = NetCDFReader(filename)
    try:
        nc.to_model(model) # type: ignore
    except ValidationError as err:
        p.print_err('ERROR')
        for e in err.errors():
            loc = ' --> ' + ' -> '.join([str(i) for i in e['loc']])
            p.print_err(f'{loc}: {e["msg"]}')
        p.print_line(LINE_LEN, '-')
        return False
    else:
        p.print('OK!')
        p.print_line(LINE_LEN, '-')
        return True

def check_against_specification(specification: str, filename: str) -> bool:
    pc = ProductChecker(specification)
    pc.check(filename)
    
    for check in pc.checks:
        p.print(f'{check.description}... ', end='')
        if check.passed:
            
            if check.has_warning:
                p.print_err('WARNING', end='')
                p.print_err(f' --> {check.warning.path}: {check.warning.message}')
            else:
                p.print('OK!')
        else:
            p.print_err('ERROR', end='')
            p.print_err(f' --> {check.error.path}: {check.error.message}')

    p.print_line_err(LINE_LEN, '=')
    p.print_err(f'{len(pc.errors)} errors found.')
    p.print_err(f'{len(pc.warnings)} warnings found.')
    p.print_line_err(LINE_LEN, '=')

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

    parser.add_argument(
        '-e',  '--error-only', action='store_true',# metavar='DEFINITION',
        help='Only print errors'
    )

    parser.add_argument(
        '-q',  '--quiet', action='store_true',# metavar='DEFINITION',
        help='Do not print any output'
    )

    args = parser.parse_args(sys.argv[2:])
    p.errors_only = args.error_only
    p.quiet = args.quiet

    check_file(args)