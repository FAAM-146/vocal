"""Check a netCDF file against standard and product definitions."""

import os
import re
import sys

from netCDF4 import Dataset
from pydantic import BaseModel
from pydantic import ValidationError
import yaml

from vocal.utils.registry import Registry

from . import parser_factory
from ..checking import ProductChecker
from ..core import register_defaults_module
from ..netcdf import NetCDFReader
from ..utils import (
    get_error_locs,
    import_project,
    TextStyles,
    Printer,
    import_versioned_project,
    regexify_file_pattern,
)
from ..utils.conventions import (
    get_conventions_string,
    read_conventions_identifier,
    extract_conventions_info,
)

LINE_LEN = 50

TS = TextStyles()
p = Printer()


def check_against_standard(
    model: BaseModel, filename: str, project_name: str = ""
) -> bool:
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
        f"Checking {TS.BOLD}{filename}{TS.ENDC} against "
        f"{TS.BOLD}{project_name}{TS.ENDC} standard... ",
        end="",
    )

    nc = NetCDFReader(filename)

    try:
        nc_noval = nc.to_model(model, validate=False)  # type: ignore
        nc.to_model(model)  # type: ignore
    except ValidationError as err:
        p.print_err(f"{TS.FAIL}{TS.BOLD}ERROR!{TS.ENDC}\n")

        error_locs = get_error_locs(err, nc_noval)

        for err_loc, err_msg in zip(*error_locs):
            p.print_err(f"{TS.FAIL}{TS.BOLD}✗{TS.ENDC} {err_loc}: {err_msg}")

        p.print_err()
        return False
    else:
        p.print_err(f"{TS.OKGREEN}{TS.BOLD}OK!{TS.ENDC}\n")

        return True


def print_checks(pc, filename, specification):
    p.print_err(
        f"Checking {TS.BOLD}{filename}{TS.ENDC} against "
        f"{TS.BOLD}{os.path.basename(specification)}{TS.ENDC} specification... ",
        end="",
    )

    failed = any(not check.passed for check in pc.checks)
    if failed:
        p.print_err(f"{TS.FAIL}{TS.BOLD}ERROR!{TS.ENDC}\n")
    else:
        p.print_err(f"{TS.OKGREEN}{TS.BOLD}OK!{TS.ENDC}\n")

    for check in pc.checks:

        if check.passed:

            if check.has_warning and check.warning:
                p.print_warn(f"  {check.description}", end="\r")
                p.print_warn(f"{TS.BOLD}{TS.WARNING}!{TS.ENDC}")
                p.print_warn(
                    f"{TS.BOLD}{TS.WARNING}  --> {check.warning.path}: "
                    f"{check.warning.message}{TS.ENDC}"
                )
            else:
                p.print(f"  {check.description}", end="\r")
                p.print(f"{TS.BOLD}{TS.OKGREEN}✔{TS.ENDC}")
        elif check.error:
            p.print_err(f"  {check.description}", end="\r")
            p.print_err(f"{TS.FAIL}{TS.BOLD}✗{TS.ENDC}")
            p.print_err(
                f"{TS.FAIL}  --> {TS.BOLD}{check.error.path}:{TS.ENDC} "
                f"{TS.FAIL}{check.error.message}{TS.ENDC}"
            )

    for comment in pc.comments:
        p.print_comment()
        p.print_comment(
            f"{TS.HEADER}{TS.BOLD}COMMENT:{TS.ENDC} {TS.HEADER}{comment.path}: "
            f"{comment.message}{TS.ENDC}"
        )

    p.print_err()
    p.print_line_err(LINE_LEN, "=")
    p.print_err(f"{TS.BOLD}{TS.OKGREEN}✔{TS.ENDC} {len(pc.checks)} checks.")
    p.print_err(f"{TS.BOLD}{TS.WARNING}!{TS.ENDC} {len(pc.warnings)} warnings.")
    p.print_err(f"{TS.BOLD}{TS.FAIL}✗{TS.ENDC} {len(pc.errors)} errors found.")
    p.print_line_err(LINE_LEN, "=")
    p.print_err()


def check_against_specification(filename: str, specification: str) -> bool:
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
    print_checks(pc, filename, specification)
    return pc.passing


def check_file_against_project(filename: str, project: str) -> bool:
    """
    Check a file against standard and/or product definition.

    Args:
        args (Namespace): The parsed command line arguments.

    Exit:
        0 if all checks pass, 1 otherwise.
    """
    p.print_err()

    try:
        project_mod = import_project(project)

    except Exception:
        try:
            regex = read_conventions_identifier(project)
            conventions_info = extract_conventions_info(filename, regex)
            project_mod = import_versioned_project(project, conventions_info)
            project = str(conventions_info)
        except Exception:
            p.print_err(f'Could not import vocal project at "{project}"')
            p.print_err("Please check that the project exists and is importable.")
            raise

    register_defaults_module(project_mod.defaults)

    return check_against_standard(
        model=project_mod.models.Dataset,
        filename=filename,
        project_name=os.path.basename(project),
    )


def load_matching_projects(filename: str) -> list[str]:
    """
    Given a filename, load all projects that match the conventions
    found in the file.

    Args:
        filename (str): The path to the netCDF file.

    Returns:
        list[str]: The paths to the matching projects.
    """
    conventions = get_conventions_string(filename)

    if conventions is None:
        p.print_err(
            f"{TS.BOLD}{TS.FAIL}✗{TS.ENDC} No conventions found in file. Please provide a project or definition.\n"
        )
        sys.exit(1)

    c = Registry.filter(conventions)

    if len(c) == 0:
        p.print_err(
            f"{TS.BOLD}{TS.FAIL}✗{TS.ENDC} No registered project(s) found for conventions {conventions}\n"
        )
        sys.exit(1)

    print(
        f"\n{TS.BOLD}{TS.OKGREEN}✔{TS.ENDC} Found {len(c)} registered project(s) for conventions {conventions}: {', '.join(c.projects.keys())}"
    )

    return [p.path for p in c.projects.values()]


def load_matching_definitions(filename: str) -> list[str]:
    """
    Given a filename, load all definitions that have registered projects
    that match the conventions found in the file.

    Args:
        filename (str): The path to the netCDF file.

    Returns:
        list[str]: The paths to the matching definition files.
    """

    conventions = get_conventions_string(filename)

    if conventions is None:
        p.print_err(
            f"{TS.BOLD}{TS.FAIL}✗{TS.ENDC} No conventions found in file. Please provide a project or definition."
        )
        sys.exit(1)

    registry = Registry.filter(conventions)

    definitions: list[str] = []
    paths: list[str] = []
    filecodecs: list[dict] = []

    # For each project, extract the conventions info and find all of the
    # definitions that have the matching version. Also, store the filecodec
    # for each project.
    for project in registry:
        ci = extract_conventions_info(
            filename, project.spec.regex, name=project.spec.name
        )
        paths.append(os.path.join(project.definitions, ci.version_string))
        vocal_project = import_project(project.path)
        filecodecs.append(vocal_project.filecodec)

    # Iterate over the definitions and filecodecs to find the matching
    # definition for the file.
    for path, codec in zip(paths, filecodecs):
        def_files = [
            f
            for f in os.listdir(path)
            if f.endswith(".json") and f != "dataset_schema.json"
        ]
        for file in def_files:
            with open(os.path.join(path, file), "r") as f:
                data = yaml.load(f, Loader=yaml.Loader)

                # Get the filename from the file pattern, and convert it to a
                # regex.
                rex = regexify_file_pattern(data["meta"]["file_pattern"], codec)

                # If the filename matches the regex, we want to use this 
                # definition.
                if re.match(rex, filename):
                    p.print_err(f"{TS.BOLD}{TS.OKGREEN}✔{TS.ENDC} Found matching definition: {file}")
                    definitions.append(os.path.join(path, file))

    if len(definitions) == 0:
        p.print_err(
            f"{TS.BOLD}{TS.WARNING}!{TS.ENDC} No definitions match for file {filename}"
        )

    return definitions


def run_checks(filename: str, projects: list[str], definitions: list[str]) -> bool:
    """
    Run all required checks on a file.

    Args:
        filename (str): The path to the netCDF file.
        projects (list[str]): The paths to the projects to check against.
        definitions (list[str]): The paths to the definitions to check against.

    Returns:
        bool: True if all checks pass, False otherwise.
    """
    ok = True
    for project in projects:

        str_project = str(project)
        if str_project.endswith("/"):
            str_project = str_project[:-1]

        ok = check_file_against_project(filename, str_project) and ok

    if definitions is not None:
        for definition in definitions:
            ok = check_against_specification(filename, definition) and ok

    return ok


def main() -> None:
    """
    Main entry point for the vocal check command.
    """

    parser = parser_factory(
        file=__file__,
        description="Check a file against standard and/or product definition",
    )

    parser.add_argument(
        "filename", type=str, metavar="FILE", help="The netCDF file to check"
    )

    parser.add_argument(
        "-p",
        "--project",
        dest="project",
        type=str,
        metavar="PROJECT",
        nargs="+",
        action="store",
        default=None,
        help="Path to one or more vocal projects, defaults to current directory",
    )

    parser.add_argument(
        "-d",
        "--definition",
        dest="definition",
        type=str,
        metavar="DEFINITION",
        nargs="+",
        default=None,
        help="Product definition(s) to test against",
    )

    parser.add_argument(
        "-e",
        "--error-only",
        action="store_true",
        help="Only print errors. Takes presidence over -w/--warnings",
    )

    parser.add_argument(
        "-w",
        "--warnings",
        action="store_true",
        help="Only print warnings and errors",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not print any output",
    )

    parser.add_argument("-c", "--comments", action="store_true", help="Print comments")

    parser.add_argument(
        "--no-color", action="store_true", help="Do not print colored output"
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

    if args.project is None:
        p.print_err()
        args.project = load_matching_projects(args.filename)

    if args.definition is None:
        args.definition = load_matching_definitions(args.filename)

    ok = run_checks(args.filename, args.project, args.definition)

    sys.exit(0 if ok else 1)
