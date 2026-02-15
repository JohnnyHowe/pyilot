import shlex
import sys
from pathlib import Path
from typing import Iterable, Optional, Union

# TODO find better solution to this
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pretty_print import *


class Command:
    executable: Optional[str] = None
    subcommands: list[str] = []
    positional_args: list[str] = []
    flags: list[Union[str, tuple[str,str]]] = []

    # ==============================================================================================
    # region Public
    # ==============================================================================================

    def add_flag_and_value(self, flag: str, value: str) -> None:
        """ Flag should include "-" prefix. """
        if not flag.startswith("-"):
            pretty_print(f"[CommandUtility] Flag added without \"-\" prefix ({flag}). Did you mean to do this?")
        self.flags.append((flag, value))

    def add_flag(self, flag: str) -> None:
        """ Flag should include "-" prefix. """
        if not flag.startswith("-"):
            pretty_print(f"[CommandUtility] Flag added without \"-\" prefix ({flag}). Did you mean to do this?")
        self.flags.append(flag)

    def to_str(self, newlines: bool = False) -> str:
        sub_commands_str = " ".join(self.subcommands)
        result = f"{self.executable} {sub_commands_str}"

        for part in self.positional_args + self.flags:
            if newlines:
                result += " \\ \n  "
            if isinstance(part, tuple):
                result += f"{part[0]} {part[1]}"
            else:
                result += part

        return result.strip()

    # ==============================================================================================
    # region Private
    # ==============================================================================================

    def as_list(self) -> list:
        return [self.executable] + self.subcommands + self.positional_args + list(self._get_flags_unpacked()) 

    def _get_flags_unpacked(self) -> Iterable:
        for part in self.flags:
            if isinstance(part, tuple):
                yield from part
            else:
                yield part

    def __str__(self) -> str:
        sub_commands_str = " ".join(self.subcommands)
        flags_str = " ".join(self.flags)
        positional_args_str = " ".join(self.positional_args)

        result = ""
        for part in [self.executable, sub_commands_str, positional_args_str, flags_str]:
            if len(part.strip()) > 0:
                result += part + " "
        return result.strip()
        