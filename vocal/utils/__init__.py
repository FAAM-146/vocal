from __future__ import annotations

import copy
import glob
import importlib
import importlib.util
import os
import re
import sys

from typing import Iterator, Optional, Type, Generator
from types import ModuleType
from dataclasses import dataclass
from contextlib import contextmanager
import netCDF4 # type: ignore

import pydantic
import yaml


def _resolve_version(version: str, product_root: str) -> str:
    """
    Resolve the version of a dataset.

    Args:
        version: the version of the dataset
        product_root: the root directory of the product

    Returns:
        the resolved version
    """
    if version == 'latest':
        return os.path.join(product_root, 'products', 'latest')
    else:
        return os.path.join(product_root, f'v{version}')
    

def _get_product_root(project: ModuleType) -> str:
    """
    Get the root directory of the product.

    Args:
        project: the vocal project

    Returns:
        the root directory of the product
    """
    if project.__file__ is None:
        raise ValueError('The vocal project must be a module')
    
    return os.path.sep.join(project.__file__.split(os.path.sep)[:-2])


def get_product(short_name, project=None, version='latest', product_root=None):
    if project is None:
        raise ValueError('The vocal project must be specified')
    
    if product_root is None:
        product_root = _get_product_root(project)

    spec = get_spec(
        short_name, project=project, version=version, product_root=product_root
    )
    return project.models.Dataset.model_validate(spec)


def get_spec(short_name, project=None, version='latest', product_root=None) -> dict | None:
    if project is None:
        raise ValueError('The vocal project must be specified')
    
    if product_root is None:
        product_root = _get_product_root(project)

    products_dir = _resolve_version(version, product_root)

    defs = [
        i for i in glob.glob(os.path.join(products_dir, '*.json'))
        if not i.endswith('dataset_schema.json')
    ]

    for d in defs:
        with open(d, 'r') as y:
            spec = yaml.load(y, Loader=yaml.Loader)
            try:
                if spec['meta']['short_name'] == short_name:
                    return spec
            except Exception:
                continue

    return None


@dataclass
class Conventions:
    name: str
    major_version: Optional[int] = None
    minor_version: Optional[int] = None

    def __str__(self) -> str:
        return f'{self.name}-{self.major_version}.{self.minor_version}'


@dataclass
class FolderManager:
    """
    A class which manages folder creation and context switching.
    """

    base_folder: str
    version: str

    def make_folder(self, folder: str) -> None:
        """
        Creates a specified folder in the current directory. If the folder
        already exists and contains any files, these files will be removed.

        Args:
            folder: the name of the folder to create
        """
        os.makedirs(folder, exist_ok=True)
        self.clean_folder(folder)

    def clean_folder(self, folder: str) -> list[str]:
        """
        Remove the contents of a given directory.

        Args:
            folder: the name of the folder to empty

        Returns:
            a list of the deleted contents of folder
        """
        _files = os.listdir(folder)
        for _file in _files:
            os.remove(os.path.join(folder, _file))
        return _files

    def _folder_name(self) -> str:
        """
        Build an output folder name

        Returns: 
            the name of the output folder
        """
        return os.path.join(self.base_folder, self.version)

    @contextmanager # type: ignore
    def in_folder(self) -> Iterator[None]:
        """
        Returns a context manager, which temporarily changes the working
        directory, creating if if it doesn't exist.
        """
        folder = self._folder_name()
        if not os.path.isdir(folder):
            self.make_folder(folder)
        
        cwd = os.getcwd()
        try:
            os.chdir(folder)
            yield
        except Exception:
            raise
        finally:
            os.chdir(cwd)

def get_type_from_placeholder(placeholder: str) -> tuple[str, str]:
        """
        Returns the type from a placeholder string. 

        Args:
            placeholder: the placeholder string

        Returns:
            An info type, for example <str>, <float32>
        """
        # rex = re.compile("<([a-z0-9]+): derived_from_file>")
        rex = re.compile('<(Array)?\[?([a-z0-9]+)\]?: derived_from_file\s?.*>')
        matches = rex.search(placeholder)
        if not matches:
            raise ValueError('Unable to get type from placeholder')

        dtype = f'<{matches.groups()[1]}>'
        container = matches.groups()[0]

        return dtype, container

def dataset_from_partial_yaml(
    
    yamlfile: str,
    variable_template: dict,
    globals_template: dict,
    group_template: dict,
    model: Type[pydantic.BaseModel],
    construct: bool = False
) -> pydantic.BaseModel:

    if model is None:
        raise ValueError('Pydantic model has not been defined')

    def parse_definition(defn: dict, ctype: str='dataset') -> dict:   

        for var in defn['variables']:
                        
            _temp = copy.deepcopy(variable_template)
            _temp.update(var['attributes'])
            var['attributes'] = _temp

        try:
            for g in defn['groups']:
                parse_definition(g, ctype='group')
        except KeyError:
            pass

        template = globals_template if ctype == 'dataset' else group_template
        _temp = copy.deepcopy(template)
        _temp.update(defn['attributes'])
        defn['attributes'] = _temp

        return defn

    with open(yamlfile, 'r') as f:
        y = yaml.load(f, Loader=yaml.Loader)

        if construct:
            return model.model_construct(**parse_definition(y))
        
        return model(**parse_definition(y))
    

def import_project(project: str) -> ModuleType:
    """
    Import a vocal project from a given path.

    Args:
        project: the path to the project

    Returns:
        the imported module
    """

    import_error_msg = f"Unable to import project {project}"

    module_path = os.path.join(project, '__init__.py')
    if not module_path.startswith('/'):
        module_path = os.path.join(os.getcwd(), module_path)


    spec = importlib.util.spec_from_file_location(f"{project}", module_path)
    if spec is None:
        raise ImportError(import_error_msg)
    try:
        if spec.loader is None:
            raise ImportError(import_error_msg)
    except AttributeError:
        raise ImportError(import_error_msg)
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def import_versioned_project(project: str, version: Conventions) -> ModuleType:
    """
    Import a version of a vocal project from a given path. If multiple *major*
    versions of the project exist, these are assumed to be in subdirectories
    named v{major_version}.

    Args:
        project: the path to the project
        version: the version of the project to import

    Returns:
        the imported module
    """
    project_path = os.path.join(project, f'v{version.major_version}')
    return import_project(project_path)


def extract_conventions_info(ncfile: str, conventions_regex: str) -> Conventions:
    """
    Extract conventions information from a netCDF file.

    Args:
        ncfile: the path to the netCDF file
        conventions_regex: the regular expression to use to extract the
            conventions information

    Returns:
        the extracted conventions information
    """
    with netCDF4.Dataset(ncfile, 'r') as nc:
        conventions = nc.getncattr('Conventions')
        matches = re.search(conventions_regex, conventions)
        if not matches:
            raise ValueError('Unable to extract conventions information')
        
        groups = matches.groupdict()

        return Conventions(
            name=groups['name'],
            major_version=int(groups['major']),
            minor_version=int(groups['minor']),
        )


def read_conventions_identifier(path: str) -> str:
    """
    Return the regular expression used to extract conventions information from
    a netCDF file.

    Args:
        path: the path to the project

    Returns:
        the regular expression
    """
    conventions_id_file = os.path.join(path, 'conventions.yaml')
    if not os.path.isfile(conventions_id_file):
        raise ValueError(f'Unable to find conventions identifier file at {conventions_id_file}')
    
    with open(conventions_id_file, 'r') as f:
        y = yaml.load(f, Loader=yaml.Loader)

    name = y['conventions']['name']
    regex = f'.*?(?P<name>{name})-(?P<major>[0-9]+)\.(?P<minor>[0-9]+),?\s?.*'
    return regex
    

def get_error_locs(err: pydantic.ValidationError, unvalidated: pydantic.BaseModel) -> tuple[list[str], list[str]]:
    """
    Get the locations of errors in a ValidationError object. Try to get the
    name of the variable that the error is associated with, if possible.

    Args:
        err: The ValidationError object
        unvalidated: The unvalidated model

    Returns:
        A list of tuples, where the first element is the location of the error
        and the second element is the error message.
    """

    return_data: tuple[list[str], list[str]] = ([], [])

    for e in err.errors():
        ncn = unvalidated.model_copy(deep=True)
        
        locs = []

        for i in e['loc']:
            current_name = None

            try:
                ncn = ncn[i] # type: ignore
            except Exception:
                pass

            try:
                ncn = getattr(ncn, i) # type: ignore
            except Exception:
                pass
                   
            try:
                current_name = ncn['meta']['name'] # type: ignore
            except (AttributeError, TypeError, KeyError):
                pass

            if i == '__root__':
                current_name = '[root validator]'

            if current_name:
                locs.append(current_name)
            else:
                locs.append(i)


        loc = 'root -> ' + ' -> '.join([str(i) for i in locs])
        return_data[0].append(loc)
        return_data[1].append(e['msg'])

    return return_data


@contextmanager
def flip_to_dir(path: str) -> Generator[str, None, None]:
    """
    A context manager which temporarily changes the working directory.

    Args:
        path: the path to change to

    Yields:
        the current working directory
    """
    if not os.path.isdir(path):
        raise ValueError(f'{path} is not a directory')

    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield cwd
    except Exception:
        raise
    finally:
        os.chdir(cwd)

@dataclass
class TextStyles:

    _HEADER: str = '\033[95m'
    _OKBLUE: str = '\033[94m'
    _OKCYAN: str = '\033[96m'
    _OKGREEN: str = '\033[92m'
    _WARNING: str = '\033[93m'
    _FAIL: str = '\033[91m'
    _ENDC: str = '\033[0m'
    _BOLD: str = '\033[1m'
    _UNDERLINE: str = '\033[4m'

    enabled: bool = True

    def __getattr__(self, name: str) -> str:
        if not self.enabled:
            return ''

        return getattr(self, f'_{name.upper()}')
    
@dataclass
class Printer:
    """
    A class for printing messages to the terminal, with options for
    suppressing certain types of messages.
    """
    quiet: bool = False
    ignore_info: bool = False
    ignore_warnings: bool = False
    comments: bool = False

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

    def print_comment(self, *args, **kwargs):
        """
        Print a comment if comments are on
        """
        if self.quiet or not self.comments:
            return
        
        print(*args, **kwargs)

    def print_warn(self, *args, **kwargs):
        """
        Print a message in not quiet or error mode.
        """
        if self.quiet or self.ignore_warnings:
            return

        print(*args, **kwargs)
