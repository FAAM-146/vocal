from abc import ABC, abstractmethod
import os
import json
import importlib
import pkgutil

from dataclasses import dataclass
from contextlib import contextmanager
from typing import Iterator, Optional, Protocol, Tuple

from pydantic.main import BaseModel

from faam_data import __version__ as version
from faam_data.dataset import Dataset
from faam_data.dimension import Dimension
from faam_data.group import Group
from faam_data.variable import Variable

BASE_FOLDER = 'vocabularies'


@dataclass
class FolderManager:
    base_folder: str
    version: str
    folder: Optional[str] = None

    def make_folder(self) -> str:
        folder = os.path.join(self.base_folder, self.version)
        os.makedirs(folder, exist_ok=True)
        self.clean_folder(folder)
        self.folder = folder
        return folder

    def clean_folder(self, folder: str) -> list[str]:
        _files = os.listdir(folder)
        for _file in _files:
            os.remove(os.path.join(folder, _file))
        return _files

    @contextmanager
    def in_folder(self) -> None:
        if self.folder is None:
            self.make_folder()
        
        cwd = os.getcwd()
        try:
            os.chdir(self.folder)
            yield self.folder
        except Exception:
            raise
        finally:
            os.chdir(cwd)


class FolderSwitcher(Protocol):
    def in_folder(self) -> None:
        ...


@dataclass
class BaseWriter(ABC):
    model: BaseModel
    name: str
    folder_manager: FolderSwitcher
    indent: Optional[int] = 2

    @property
    @abstractmethod
    def _json(self) -> str:
        pass

    def write(self) -> None:
        _filename = f'{self.name}.json'
        with self.folder_manager.in_folder():
            mode = 'w' if not os.path.exists(_filename) else 'a'
            with open(f'{self.name}.json', mode) as f:
                f.write(self._json)


class InstanceWriter(BaseWriter):

    @property
    def _json(self) -> str:
        _dict = self.model.dict(exclude_unset=True)
        return json.dumps(_dict, indent=self.indent)


class SchemaWriter(BaseWriter):

    @property
    def _json(self) -> str:
        return json.dumps(self.model.schema(), indent=self.indent)


class DictWriter(BaseWriter):

    @property
    def _json(self) -> str:
        return json.dumps(self.model, indent=self.indent)


@dataclass
class DatasetDiscoverer:
    module_path: Optional[str] = 'faam_data.definitions'

    def discover(self) -> Iterator[Tuple[str, Dataset]]:
        modules = importlib.import_module(self.module_path)

        for i in pkgutil.iter_modules(modules.__path__):
            if not i.ispkg:
                continue
            
            name = i.name
            full_path = '.'.join((self.module_path, name, 'dataset'))
            module = importlib.import_module(full_path)
            dataset = getattr(module, 'dataset')

            yield (name, dataset)


@dataclass
class DimensionDiscoverer:
    module_path: Optional[str] = 'faam_data.definitions.dimensions'

    def discover(self) -> Iterator[Dimension]:
        module = importlib.import_module(self.module_path)
        for member_name in dir(module):
            member = getattr(module, member_name)
            if isinstance(member, Dimension):
                yield member
           

def write_datasets(folder_manager: FolderSwitcher) -> None:
    for name, dataset in DatasetDiscoverer().discover():
        writer = InstanceWriter(
            model=dataset, name=name, folder_manager=folder_manager
        )
        writer.write()

def write_dimensions(folder_manager: FolderSwitcher) -> None:
    dims = []
    for dimension in DimensionDiscoverer().discover():
        dims.append(dimension.dict())
    writer = DictWriter(
        model=dims, name='dimensions', folder_manager=folder_manager
    )
    writer.write()

def write_schemata(folder_manager: FolderSwitcher) -> None:
    models = (Dataset, Group, Variable)
    names = ('dataset_schema', 'group_schema', 'variable_schema')

    for model, name in zip(models, names):
        writer = SchemaWriter(
            model=model, name=name, folder_manager=folder_manager
        )
        writer.write()


if __name__ == '__main__':
    versions = (f'v{version}', 'latest')

    for version in versions:
        folder_manager = FolderManager(base_folder=BASE_FOLDER, version=version)
        write_datasets(folder_manager)
        write_schemata(folder_manager)
        write_dimensions(folder_manager)
    

    