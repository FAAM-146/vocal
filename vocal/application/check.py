"""Check a netCDF file against standard and product definitions."""

import os
import sys

from argparse import Namespace

from pydantic import BaseModel
from pydantic import ValidationError


from . import parser_factory
from ..checking import ProductChecker
from ..core import register_defaults_module
from ..netcdf import NetCDFReader
from ..utils import extract_conventions_info, get_error_locs, import_project, TextStyles, Printer, import_versioned_project, read_conventions_identifier

LINE_LEN = 50

TS = TextStyles()
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

    p.print_err(
        f'Checking {TS.BOLD}{filename}{TS.ENDC} against '
        f'{TS.BOLD}{project_name}{TS.ENDC} standard... ',
        end=''
    )

    nc = NetCDFReader(filename)
    
    try:
        nc_noval = nc.to_model(model, validate=False) # type: ignore
        nc.to_model(model) # type: ignore
    except ValidationError as err:
        p.print_err(f'{TS.FAIL}{TS.BOLD}ERROR!{TS.ENDC}\n')

        error_locs = get_error_locs(err, nc_noval)

        for err_loc, err_msg in zip(*error_locs):
            p.print_err(f'{TS.FAIL}{TS.BOLD}✗{TS.ENDC} {err_loc}: {err_msg}')

        p.print_err()
        return False
    else:
        p.print_err(f'{TS.OKGREEN}{TS.BOLD}OK!{TS.ENDC}\n')

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

    p.print_err(
        f'Checking {TS.BOLD}{filename}{TS.ENDC} against '
        f'{TS.BOLD}{os.path.basename(specification)}{TS.ENDC} specification... ',
        end=''
    )

    failed = any(not check.passed for check in pc.checks)
    if failed:
        p.print_err(f'{TS.FAIL}{TS.BOLD}ERROR!{TS.ENDC}\n')
    else:
        p.print_err(f'{TS.OKGREEN}{TS.BOLD}OK!{TS.ENDC}\n')
    
    for check in pc.checks:
        
        if check.passed:
            
            if check.has_warning and check.warning:
                p.print_warn(f'  {check.description}', end='\r')
                p.print_warn(f'{TS.BOLD}{TS.WARNING}!{TS.ENDC}')
                p.print_warn(
                    f'{TS.BOLD}{TS.WARNING}  --> {check.warning.path}: '
                    f'{check.warning.message}{TS.ENDC}'
                )
            else:
                p.print(f'  {check.description}', end='\r')
                p.print(f'{TS.BOLD}{TS.OKGREEN}✔{TS.ENDC}')
        elif check.error:
            p.print_err(f'  {check.description}', end='\r')
            p.print_err(f'{TS.FAIL}{TS.BOLD}✗{TS.ENDC}')
            p.print_err(
                f'{TS.FAIL}  --> {TS.BOLD}{check.error.path}:{TS.ENDC} '
                f'{TS.FAIL}{check.error.message}{TS.ENDC}'
            )

    for comment in pc.comments:
        p.print_comment()
        p.print_comment(
            f'{TS.HEADER}{TS.BOLD}COMMENT:{TS.ENDC} {TS.HEADER}{comment.path}: '
            f'{comment.message}{TS.ENDC}'
        )

    p.print_err()
    p.print_line_err(LINE_LEN, '=')
    p.print_err(f'{TS.BOLD}{TS.OKGREEN}✔{TS.ENDC} {len(pc.checks)} checks.')
    p.print_err(f'{TS.BOLD}{TS.WARNING}!{TS.ENDC} {len(pc.warnings)} warnings.')
    p.print_err(f'{TS.BOLD}{TS.FAIL}✗{TS.ENDC} {len(pc.errors)} errors found.')
    p.print_line_err(LINE_LEN, '=')
    p.print_err()

    return pc.passing


def check_file(args: Namespace) -> None:
    """
    Check a file against standard and/or product definition.

    Args:
        args (Namespace): The parsed command line arguments.

    Exit:
        0 if all checks pass, 1 otherwise.
    """
    p.print_err()

    all_ok1 = []
    for proj in args.project:
        if proj.endswith('/'):
            proj = proj[:-1]

        try:
            project = import_project(proj)

        except Exception:
            try:
                regex = read_conventions_identifier(proj)
                conventions_info = extract_conventions_info(args.filename, regex)
                project = import_versioned_project(proj, conventions_info)
                proj = str(conventions_info)
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
        file=__file__,
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

    parser.add_argument(
        '-c', '--comments', action='store_true',
        help='Print comments'
    )

    parser.add_argument(
        '--no-color', action='store_true',
        help='Do not print colored output'
    )

    args = parser.parse_args(sys.argv[2:])
    if args.error_only:
        p.ignore_info = True
        p.ignore_warnings = True
    if args.warnings:
        p.ignore_info = True
    if args.comments:
        p.comments = True

    p.quiet = args.quiet

    if args.no_color:
        TS.enabled = False

    check_file(args)