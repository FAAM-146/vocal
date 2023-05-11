from __future__ import annotations

import copy
import importlib
import importlib.util
import os
import re
import sys

from typing import Iterator, Type, Generator
from types import ModuleType
from dataclasses import dataclass
from contextlib import contextmanager

import pydantic
import yaml


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

def get_type_from_placeholder(placeholder: str) -> str:
        """
        Returns the type from a placeholder string. 

        Args:
            placeholder: the placeholder string

        Returns:
            An info type, for example <str>, <float32>
        """
        # rex = re.compile("<([a-z0-9]+): derived_from_file>")
        rex = re.compile('<(Array)?\[?([a-z0-9]+)\]?: derived_from_file>')
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
            return model.construct(**parse_definition(y))
        
        return model(**parse_definition(y))
    

def import_project(project: str) -> ModuleType:

    module_path = os.path.join(project, '__init__.py')
    if not module_path.startswith('/'):
        module_path = os.path.join(os.getcwd(), module_path)


    spec = importlib.util.spec_from_file_location(f"{project}", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module

def get_error_locs(err: pydantic.ValidationError, unvalidated: pydantic.BaseModel) -> list[tuple[str], tuple[str]]:
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

    return_data = ([], [])
    for e in err.errors():
        ncn = unvalidated.copy(deep=True)
        
        locs = []

        for i in e['loc']:
            current_name = None

            try:
                ncn = ncn[i]
            except Exception:
                pass

            try:
                ncn = getattr(ncn, i)
            except Exception:
                pass
                   
            try:
                current_name = ncn['meta']['name']
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