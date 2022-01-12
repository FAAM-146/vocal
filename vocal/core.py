from __future__ import annotations

import os

from dataclasses import dataclass, field
from typing import Any, Iterator, Optional, Protocol, Tuple, Type
import pydantic

from pydantic.error_wrappers import ValidationError

from .utils import FolderManager, dataset_from_partial_yaml
from .attributes import AttributesSet
from .writers import VocabularyCreator
from .variable import Variable
from .group import Group
from .dataset import Dataset
from .netcdf import NetCDFReader

ATTRIBUTE_TYPES = ('group', 'variable', 'globals')

_templates = {i: {} for i in ATTRIBUTE_TYPES}


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


@dataclass
class DataModel:
    """
    DataModel acts as a wrapper around a pydantic Dataset model, allowing the
    specification of custom attribute collections as types.
    """

    attributes_module: Optional[HasAttributesMembers] = None
    model: Optional[Type[Dataset]] = None
    _Group: Optional[Type[Group]] = None
    _Variable: Optional[Type[Variable]] = None

    def __post_init__(self):
        if self.attributes_module is not None:
            self.register_attributes_module(self.attributes_module)

    def check_file(self, filename: str) -> pydantic.BaseModel:
        return NetCDFReader(filename).to_model(self.model)

    def register_attributes_module(self, module: HasAttributesMembers) -> None:
        self.register_attributes(
            variable_attributes=module.VariableAttributes,  # type: ignore
            group_attributes=module.GroupAttributes,        # type: ignore
            global_attributes=module.GlobalAttributes       # type: ignore
        )

    def register_attributes(
        self,
        variable_attributes: Type[AttributesSet],
        group_attributes: Type[AttributesSet],
        global_attributes: Type[AttributesSet],
    ) -> None:
        
        # This is hideous, hacky, and probably broken. Totally blaming Graeme
        # for making me generalize this :)
        class _Variable(Variable):
            attributes: variable_attributes # type: ignore
        class _Group(Group):
            attributes: group_attributes # type: ignore
            variables: list[_Variable] # type: ignore
            groups: list[_Group] # type: ignore
        class _Dataset(Dataset):
            attributes: global_attributes # type: ignore
            variables: list[_Variable]  # type: ignore
            groups: Optional[list[_Group]] # type: ignore
        _Group.update_forward_refs(**locals())
        _Dataset.update_forward_refs(**locals())
        _Variable.update_forward_refs(**locals())

        self.model = _Dataset
        self._Group = _Group
        self._Variable = _Variable


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
    model: DataModel

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

    def create_example_file(self) -> None:
        self().create_example_file() # type: ignore

    def validate(self) -> None:
        errors = False
        try:
            self()
        except ValidationError as err:
            errors = True
            print(f'Error in dataset: {self.path}')
            for e in err.errors():
                loc = ' -> '.join([str(i) for i in e['loc']])
                print(f'{loc}: {e["msg"]}')

        if errors:
            raise ValueError('Failed to validate dataset')


@dataclass
class ProductCollection:

    model: DataModel
    version: str
    vocab_creator: Optional[SupportsCreateVocabulary] = None
    definitions: list[ProductDefinition] = field(default_factory=list)
    
    def __post_init__(self):
        if self.vocab_creator is None:
            self.vocab_creator = VocabularyCreator(
                self, FolderManager, 'vocabularies', self.version
            )

    def add_product(self, path: str) -> None:
        product = ProductDefinition(path, self.model)
        self.definitions.append(product)

    @property
    def datasets(self) -> Iterator[Tuple[str, pydantic.BaseModel]]:
        for defn in self.definitions:
            name = os.path.basename(defn.path.split('.')[0])
            yield name, defn.construct()

    def write_vocabularies(self):
        for defn in self.definitions:
            defn.validate()
        self.vocab_creator.create_vocabulary()  