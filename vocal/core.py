from __future__ import annotations

import os

from dataclasses import dataclass, field
from tkinter import N
from typing import Any, Iterator, Optional, Protocol, Tuple, Type
import pydantic

from pydantic.error_wrappers import ValidationError
# from pydantic.main import create_model

from .utils import FolderManager, dataset_from_partial_yaml
# from .attributes import AttributesSet
from .writers import VocabularyCreator
# from .variable import Variable as _Variable
# from .group import Group as _Group
# from .dataset import Dataset as _Dataset
# from .netcdf import NetCDFReader
# from vocal import group
from .utils import get_error_locs

ATTRIBUTE_TYPES = ('group', 'variable', 'globals')

_templates: dict[str, Any] = {i: {} for i in ATTRIBUTE_TYPES}


class SupportsCreateVocabulary(Protocol):
    def create_vocabulary(self) -> None:
        ...

class HasAttributesMembers(Protocol):
    GlobalAttributes: pydantic.BaseModel
    VariableAttributes: pydantic.BaseModel
    GroupAttributes: pydantic.BaseModel

class HasRequiredAttributesMembers(Protocol):
    default_globals_attrs: dict[str, Any]
    default_group_attrs: dict[str, Any]
    default_variable_attrs: dict[str, Any]


def register_defaults(name: str, mapping: dict) -> None:
    f"""
    Register a dictionary of default values
    """
    if name not in ATTRIBUTE_TYPES:
        raise ValueError('Invalid name')
    _templates[name] = mapping

def register_defaults_module(module: HasRequiredAttributesMembers) -> None:
    register_defaults('globals', getattr(module, 'default_global_attrs'))
    register_defaults('group', getattr(module, 'default_group_attrs'))
    register_defaults('variable', getattr(module, 'default_variable_attrs'))

@dataclass
class ProductDefinition:

    path: str
    model: Type[pydantic.BaseModel]

    def __call__(self) -> pydantic.BaseModel:
        return self._from_yaml(construct=False)

    def construct(self) -> pydantic.BaseModel:
        return self._from_yaml(construct=True)

    def _from_yaml(self, construct: bool=True) -> pydantic.BaseModel:

        return dataset_from_partial_yaml(
            self.path, variable_template=_templates['variable'],
            group_template=_templates['group'],
            globals_template=_templates['globals'],
            model=self.model,
            construct=construct
        )

    def create_example_file(self, nc_filename: str, find_coords: bool=False) -> None:

        
        coordinates = self.coordinates() if find_coords else None

        self().create_example_file(
            nc_filename, coordinates=coordinates
        ) # type: ignore

    def coordinates(self) -> str:
        dataset = self()

        _coords = {
            'latitude': None,
            'longitude': None,
            'altitude': None,
            'time': None
        }

        for var in dataset.variables:
            for _crd in _coords.keys():
                if var.attributes.standard_name == _crd:
                    _coords[_crd] = var.meta.name

        coord_arr = [v for _, v in _coords.items() if v]
        
        coord_str = ' '.join(coord_arr)
        
        return coord_str
        

    def validate(self) -> None:
        errors = False
        try:
            self()
        except ValidationError as err:
            nc_noval = self.construct()

            errors = True
            print(f'Error in dataset: {self.path}')

            error_locs = get_error_locs(err, nc_noval)
            for err_loc, err_msg in zip(*error_locs):
                print(f'{err_loc}: {err_msg}')

        if errors:
            raise ValueError('Failed to validate dataset')


@dataclass
class ProductCollection:

    model: Type[pydantic.BaseModel]
    version: str
    vocab_creator: Optional[SupportsCreateVocabulary] = None
    definitions: list[ProductDefinition] = field(default_factory=list)
    
    def __post_init__(self):
        if self.vocab_creator is None:
            self.vocab_creator = VocabularyCreator(
                self, FolderManager, 'products', self.version
            )

    def add_product(self, path: str) -> None:
        product = ProductDefinition(path, self.model)
        self.definitions.append(product)

    @property
    def datasets(self) -> Iterator[Tuple[str, pydantic.BaseModel]]:
        for defn in self.definitions:
            name = os.path.basename(defn.path).split('.')[0]
            yield name, defn.construct()

    def write_product_definitions(self):
        for defn in self.definitions:
            defn.validate()
        self.vocab_creator.create_vocabulary()  