import os
import re
import yaml

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator


def get_default_registry_path() -> str:
    home = os.path.expanduser("~")
    return os.path.join(home, ".vocal", "vocal-registry.yaml")


@dataclass
class ProjectSpec:
    name: str
    has_major: bool
    has_minor: bool
    regex: str

    @classmethod
    def from_dict(cls, d: dict) -> "ProjectSpec":
        return cls(
            name=d["name"],
            has_major=d["has_major"],
            has_minor=d["has_minor"],
            regex=d["regex"],
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "has_major": self.has_major,
            "has_minor": self.has_minor,
            "regex": self.regex,
        }


@dataclass
class Project:
    spec: ProjectSpec
    path: str
    definitions: str

    @classmethod
    def from_dict(cls, d: dict) -> "Project":
        return cls(
            spec=ProjectSpec.from_dict(d["spec"]),
            path=d["path"],
            definitions=d["definitions"],
        )

    def to_dict(self) -> dict:
        return {
            "spec": self.spec.to_dict(),
            "path": self.path,
            "definitions": self.definitions,
        }


@dataclass
class Registry:
    projects: dict[str, Project]

    def __iter__(self):
        return iter(self.projects)

    def __getitem__(self, key: str) -> Project:
        return self.projects[key]

    def __len__(self) -> int:
        return len(self.projects)

    def first(self) -> Project:
        return next(iter(self.projects.values()))

    @classmethod
    def from_dict(cls, d: dict) -> "Registry":
        return cls(projects={k: Project.from_dict(v) for k, v in d.items()})

    @classmethod
    def load(cls, path: str) -> "Registry":
        with open(path, "r") as f:
            try:
                return cls.from_dict(yaml.load(f, Loader=yaml.Loader))
            except AttributeError:
                return cls(projects={})

    def to_dict(self) -> dict:
        return {k: v.to_dict() for k, v in self.projects.items()}

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            yaml.dump(self.to_dict(), f)

    def add_project(self, project: Project, force: bool = False) -> None:
        if project.spec.name in self.projects and not force:
            raise ValueError(f"Project {project.spec.name} is already registered.")
        self.projects[project.spec.name] = project

    def remove_project(self, name: str) -> None:
        del self.projects[name]

    @classmethod
    @contextmanager
    def open(
        cls, path: str = get_default_registry_path()
    ) -> Generator["Registry", None, None]:
        registry = cls.load(path)
        yield registry
        registry.save(path)

    @classmethod
    def filter(
        cls, conventions_string: str, path: str = get_default_registry_path()
    ) -> "Registry":
        projects = {}
        registry = cls.load(path)

        conventions = conventions_string.split(" ")
        for project in registry:
            spec = registry.projects[project].spec
            for conv in conventions:
                if re.match(spec.regex, conv):
                    projects[project] = registry.projects[project]
                    break

        return cls(projects=projects)
