from abc import ABC, abstractmethod
import os
import json
import importlib
import pkgutil

from dataclasses import dataclass
from contextlib import contextmanager
from typing import Any, Container, ContextManager, Iterator, Optional,  Protocol, Tuple, Type
from pydantic.error_wrappers import ValidationError

from pydantic.main import BaseModel

from faam_data import __version__ as version
from faam_data import dataset
from faam_data.dataset import Dataset
from faam_data.dimension import Dimension
from faam_data.group import Group
from faam_data.variable import Variable

BASE_FOLDER = 'vocabularies'


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


class SupportsInFolder(Protocol):
    def in_folder(self) -> ContextManager[None]:
        ...


@dataclass # type: ignore # mypy issue with abstract dataclasses
class BaseWriter(ABC):
    """
    An abstract class, defining an interface for writing vocabs to file.
    """
    
    model: Any 
    name: str
    folder_manager: SupportsInFolder
    indent: int = 2

    @property
    @abstractmethod
    def _json(self) -> str:
        """
        return a string json representation of model
        """
        return NotImplemented

    def write(self) -> None:
        """
        Write the model to file, as json, in a location given by folder_manager
        """
        _filename = f'{self.name}.json'
        with self.folder_manager.in_folder():
            mode = 'w' if not os.path.exists(_filename) else 'a'
            with open(f'{self.name}.json', mode) as f:
                f.write(self._json)


class InstanceWriter(BaseWriter):
    """
    Implements a writer intended to write out model instances to file.
    """

    model: BaseModel

    @property
    def _json(self) -> str:
        _dict = self.model.dict(exclude_unset=True)
        return json.dumps(_dict, indent=self.indent)


class SchemaWriter(BaseWriter):
    """
    Implements a writer intended to write model schema to file.
    """

    model: BaseModel

    @property
    def _json(self) -> str:
        return json.dumps(self.model.schema(), indent=self.indent)


class ContainerWriter(BaseWriter):
    """
    Implements a writer indended to write native containers to file. 
    Assumes that these will be json serializable.
    """

    model: Container

    @property
    def _json(self) -> str:
        return json.dumps(self.model, indent=self.indent)


@dataclass
class DatasetDiscoverer:
    """
    Class for discovering dataset definitions.
    """

    module_path: str = 'faam_data.definitions'

    def discover(self) -> Iterator[Tuple[str, Dataset]]:
        """
        Return a generator which yields 2-tuples of dataset name and dataset
        """

        modules = importlib.import_module(self.module_path)

        for i in pkgutil.iter_modules(modules.__path__): # type: ignore
            if not i.ispkg:
                continue
            
            name = i.name
            full_path = '.'.join((self.module_path, name))
            module = importlib.import_module(full_path)
            dataset = getattr(module, 'dataset')

            yield (name, dataset)


@dataclass
class DimensionDiscoverer:
    """
    Class for discovering dimension definitions
    """

    module_path: str = 'faam_data.definitions.dimensions'

    def discover(self) -> Iterator[Dimension]:
        """
        Returns a generator which yields Dimensions which have been defined in
        module_path.
        """
        module = importlib.import_module(self.module_path)
        for member_name in dir(module):
            member = getattr(module, member_name)
            if isinstance(member, Dimension):
                yield member
           

@dataclass
class VocabularyCreator:

    folder_manager: Type[FolderManager]
    base_folder: str
    version: str

    def write_datasets(self, folder_manager: SupportsInFolder) -> None:
        """
        Write defined datasets to file.
        """
        for name, dataset in DatasetDiscoverer().discover():
            writer = InstanceWriter(
                model=dataset, name=name, folder_manager=folder_manager
            )
            writer.write()

    def write_dimensions(self, folder_manager: SupportsInFolder) -> None:
        """
        Write defined dimensions to file.
        """
        dims = []
        for dimension in DimensionDiscoverer().discover():
            dims.append(dimension.dict())
        writer = ContainerWriter(
            model=dims, name='dimensions', folder_manager=folder_manager
        )
        writer.write()

    def write_schemata(self, folder_manager: SupportsInFolder) -> None:
        """
        Write dataset, group, and variable schemata to file.
        """
        models = (Dataset, Group, Variable)
        names = ('dataset_schema', 'group_schema', 'variable_schema')

        for model, name in zip(models, names):
            writer = SchemaWriter(
                model=model, name=name, folder_manager=folder_manager
            )
            writer.write()

    def create_vocabulary(self) -> None:
        """
        Create vocabularies.
        """
        versions = (f'v{self.version}', 'latest')

        for version in versions:
            folder_manager = self.folder_manager(
                base_folder=self.base_folder, version=version
            )
            self.write_datasets(folder_manager)
            self.write_schemata(folder_manager)
            self.write_dimensions(folder_manager)


@dataclass
class BasicDatasetValidator:

    errors = False

    def validate(self) -> None:
        """
        Perform a very basic check of the defined datasets, via a round trip
        the dict and back. This can catch some errors as the datasets are
        build through construct, which does no validation. The round trip
        will force validation to be performed.
        """
        for ds in DatasetDiscoverer().discover():
            try:
                Dataset(**ds[1].dict(by_alias=True))
            except ValidationError as err:
                self.errors = True
                print(f'Error in dataset: {ds[0]}')
                for e in err.errors():
                    loc = ' -> '.join([str(i) for i in e['loc']])
                    print(f'{loc}: {e["msg"]}')
        if self.errors:
            raise ValueError('Failed to validate all datasets')
        

if __name__ == '__main__':
    BasicDatasetValidator().validate()
    creator = VocabularyCreator(FolderManager, BASE_FOLDER, version)
    creator.create_vocabulary()   

    