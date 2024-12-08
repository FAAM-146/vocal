#!/usr/bin/env python

import os
import sys
import importlib
from types import ModuleType
from typing import Never

from vocal.application import commands

APPLICATION_PATH = "vocal.application"
E_CMDLINE = 2
E_GENERAL = 1


def get_descriptions() -> list:
    return [
        importlib.import_module(".".join((APPLICATION_PATH, cmd))).__doc__
        for cmd in commands
    ]


def print_help_and_exit(code: int = 0) -> Never:
    print("\nAvailable commands are:\n")
    for cmd, desc in zip(commands, get_descriptions()):
        print(f"* {cmd:15s} - {desc}")
    print()
    print('try "vocal <command> -h" for help\n')
    sys.exit(code)


def get_command() -> str:
    try:
        return sys.argv[1]
    except IndexError:
        print_help_and_exit(code=E_CMDLINE)


def get_prog_module(cmd: str) -> ModuleType:
    mod_path = ".".join((APPLICATION_PATH, cmd))
    try:
        return importlib.import_module(mod_path)
    except ModuleNotFoundError:
        print_help_and_exit(code=E_CMDLINE)


def main() -> None:

    debug = os.environ.get("VOCAL_DEBUG", "false").lower() == "true"

    try:
        get_prog_module(get_command()).main()
    except Exception as e:
        if debug:
            raise
        print(f"Error: {e.args[0]}")
        sys.exit(E_GENERAL)

    sys.exit(0)


if __name__ == "__main__":
    main()
