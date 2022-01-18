from __future__ import annotations

import copy
import os
from typing import Any, Iterator, Mapping, TYPE_CHECKING, Type
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
        print(ctype)
        print(defn)

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