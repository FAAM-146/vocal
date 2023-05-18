"""Check a netCDF file against standard and product definitions."""

from argparse import Namespace
from dataclasses import dataclass
import importlib
import os
import sys

from pydantic.error_wrappers import ValidationError

from vocal.core import register_defaults_module
from vocal.netcdf import NetCDFReader
from vocal.checking import ProductChecker
from vocal.utils import import_project
from pydantic import BaseModel

from . import parser_factory
from ..utils import get_error_locs

LINE_LEN = 50


@dataclass
class Printer:
    """
    A class for printing messages to the terminal, with options for
    suppressing certain types of messages.
    """
    quiet: bool = False
    ignore_info: bool = False
    ignore_warnings: bool = False

    def print_line(self, len: int=50, token: str='-'):
        """
        Print a line of a given length, with a given token.

        Args:
            len (int): The length of the line.
            token (str): The token to use.

        Returns:
            None
        """
        if self.quiet or self.ignore_info:
            return
        print(token * len)

    def print_line_err(self, len: int=50, token: str='-'):
        """
        Print a line of a given length, with a given token.

        Args:
            len (int): The length of the line.
            token (str): The token to use.

        Returns:
            None
        """
        if self.quiet:
            return
        print(token * len)

    def print(self, *args, **kwargs):
        """
        Print a message.
        """
        if self.quiet or self.ignore_info:
            return

        print(*args, **kwargs)
        
    def print_err(self, *args, **kwargs):
        """
        Print a message in not quiet mode.
        """
        if self.quiet:
            return

        print(*args, **kwargs)

    def print_warn(self, *args, **kwargs):
        """
        Print a message in not quiet or error mode.
        """
        if self.quiet or self.ignore_warnings:
            return

        print(*args, **kwargs)


p = Printer()


def check_against_standard(model: BaseModel, filename: str, project_name: str='') -> bool:
    """
    Check a netCDF file against a standard (a vocal/pydantic model).

    Args:
        model (BaseModel): The model to check against.
        filename (str): The path of the netCDF file to check.
        project_name (str): The name of the project to check against.

    Returns:
        bool: True if all checks pass, False otherwise.
    """

    p.print_line(LINE_LEN, '-')
    p.print(f'Checking {filename} against {project_name} standard... ', end='')
    nc = NetCDFReader(filename)
    
    try:
        nc_noval = nc.to_model(model, validate=False) # type: ignore
        nc.to_model(model) # type: ignore
    except ValidationError as err:
        p.print_err('ERROR')

        error_locs = get_error_locs(err, nc_noval)

        for err_loc, err_msg in zip(*error_locs):
            p.print_err(f'{err_loc}: {err_msg}')

        p.print_line(LINE_LEN, '-')
        return False
    else:
        p.print('OK!')
        p.print_line(LINE_LEN, '-')
        return True


def check_against_specification(specification: str, filename: str) -> bool:
    """
    Check a netCDF file against a product specification.

    Args:
        specification (str): The path of the specification to check against.
        filename (str): The path of the netCDF file to check.

    Returns:
        bool: True if all checks pass, False otherwise.
    """
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
    """
    Check a file against standard and/or product definition.

    Args:
        args (Namespace): The parsed command line arguments.

    Exit:
        0 if all checks pass, 1 otherwise.
    """

    all_ok1 = []
    for proj in args.project:
        try:
            project = import_project(proj) 
        except Exception:
            p.print_err(f'Could not import vocal project at "{proj}"')
            p.print_err('Please check that the project exists and is importable.')
            raise
        register_defaults_module(project.defaults)
        all_ok1.append(
            check_against_standard(
                model=project.models.Dataset, filename=args.filename,
                project_name=os.path.basename(proj)
            )
        )

    ok1 = all(all_ok1)
    ok2 = True

    if args.definition:
        ok2 = check_against_specification(args.definition, args.filename)

    sys.exit(int(not (ok1 and ok2)))
        

def main() -> None:
    """
    Main entry point for the vocal check command.
    """

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
        nargs='+', action='store', default=['.'],
        help='Path to one or more vocal projects, defaults to current directory'
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