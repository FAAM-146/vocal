"""Check a netCDF file against standard and product definitions."""

from argparse import Namespace
from dataclasses import dataclass
import importlib
import sys

from pydantic.error_wrappers import ValidationError

from vocal.core import register_defaults_module
from vocal.netcdf import NetCDFReader
from vocal.checking import ProductChecker
from vocal.utils import import_project
from pydantic import BaseModel

from . import parser_factory

LINE_LEN = 50


@dataclass
class Printer:
    quiet: bool = False
    ignore_info: bool = False
    ignore_warnings: bool = False

    def print_line(self, len: int=50, token: str='-'):
        if self.quiet or self.ignore_info:
            return
        print(token * len)

    def print_line_err(self, len: int=50, token: str='-'):
        if self.quiet:
            return
        print(token * len)

    def print(self, *args, **kwargs):
        if self.quiet or self.ignore_info:
            return

        print(*args, **kwargs)
        
    def print_err(self, *args, **kwargs):
        if self.quiet:
            return

        print(*args, **kwargs)

    def print_warn(self, *args, **kwargs):
        if self.quiet or self.ignore_warnings:
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
                p.print_warn('WARNING', end='')
                p.print_warn(f' --> {check.warning.path}: {check.warning.message}')
            else:
                p.print('OK!')
        else:
            p.print_err('ERROR', end='')
            p.print_err(f' --> {check.error.path}: {check.error.message}')

    p.print_line_err(LINE_LEN, '=')
    p.print_err(f'{len(pc.checks)} checks.')
    p.print_err(f'{len(pc.warnings)} warnings.')
    p.print_err(f'{len(pc.errors)} errors found.')
    p.print_line_err(LINE_LEN, '=')

    return pc.passing


def check_file(args: Namespace) -> None:

    project = import_project(args.project)

    register_defaults_module(project.defaults)
    ok1 = check_against_standard(model=project.models.Dataset, filename=args.filename)

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
        help='Only print errors. Takes presidence over -w/--warnings'
    )

    parser.add_argument(
        '-w',  '--warnings', action='store_true',# metavar='DEFINITION',
        help='Only print warnings and errors'
    )

    parser.add_argument(
        '-q',  '--quiet', action='store_true',# metavar='DEFINITION',
        help='Do not print any output'
    )

    args = parser.parse_args(sys.argv[2:])
    if args.error_only:
        p.ignore_info = True
        p.ignore_warnings = True
    if args.warnings:
        p.ignore_info = True

    p.quiet = args.quiet

    check_file(args)