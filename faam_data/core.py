from __future__ import annotations

import os

from dataclasses import dataclass, field
from typing import Iterator, Mapping, Optional, Protocol, Type

from pydantic.error_wrappers import ValidationError

from .utils import FolderManager, dataset_from_partial_yaml
from .attributes import AttributesSet
from .writers import VocabularyCreator
from .variable import Variable
from .group import Group
from .dataset import Dataset


class SupportsCreateVocabulary(Protocol):
    def create_vocabulary(self) -> None:
        ...


@dataclass
class DataModel:
    """
    DataModel acts as a wrapper around a pydantic Dataset model, allowing the
    specification of custom attribute collections as types.
    """

    model: Optional[Type[Dataset]] = None
    _Group: Optional[Type[Group]] = None
    _Variable: Optional[Type[Variable]] = None

    def register_attributes(
        self,
        variable_attributes: AttributesSet,
        group_attributes: AttributesSet,
        global_attributes: AttributesSet,
    ) -> None:
        
        # This is hideous, hacky, and probably broken. Totally blaming Graeme
        # for making me generalize this :)
        class _Variable(Variable):
            attributes: variable_attributes
        class _Group(Group):
            attributes: group_attributes
            variables: list[_Variable]
            groups: list[_Group]
        class _Dataset(Dataset):
            attributes: global_attributes
            variables: list[_Variable]
            groups: Optional[list[_Group]]
        _Group.update_forward_refs(**locals())
        _Dataset.update_forward_refs(**locals())
        _Variable.update_forward_refs(**locals())

        self.model = _Dataset
        self._Group = _Group
        self._Variable = _Variable

_templates = {}
def register_template(name: str, mapping: Mapping) -> None:
    if name not in ('group', 'variable', 'globals'):
        raise ValueError('Invalid name')
    _templates[name] = mapping

@dataclass
class ProductDefinition:

    path: str
    model: DataModel

    def __call__(self) -> Dataset:
        return self._from_yaml(construct=False)

    def construct(self) -> Dataset:
        return self._from_yaml(construct=True)

    def _from_yaml(self, construct: bool=True) -> Dataset:

        return dataset_from_partial_yaml(
            self.path, variable_template=_templates['variable'],
            group_template=_templates['group'],
            globals_template=_templates['globals'],
            model=self.model,
            construct=construct
        )

    def create_example_file(self) -> None:
        self().create_example_file()

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
    def datasets(self) -> Iterator[DataModel]:
        for defn in self.definitions:
            name = os.path.basename(defn.path.split('.')[0])
            yield name, defn.construct()

    def write_vocabularies(self):
        self.vocab_creator.create_vocabulary()  