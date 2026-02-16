"""
Ensures all parameters are accounted for.
In order of priority
 - CLI args
 - Environment variables
 - Defaults (if they exist)

raises ??? if required parameters do not exist.
"""

import argparse
from enum import Enum
import os
from pathlib import Path
from typing import get_type_hints
from python_command_line_helpers.arg_casting import cast_cli_arg
from python_command_line_helpers import input_cleaning
from python_pretty_print import pretty_print


class ParameterSource(Enum):
    CLI = 0,
    ENV = 1,
    DEFAULTS = 3
    NONE = 4


class UploadParameters:
    api_key_issuer_id: str
    api_key_id: str
    api_key_content: str
    output_directory: Path
    groups: list[str] = []
    changelog: str
    max_upload_attempts: int = 10
    attempt_timeout: int = 600  # seconds

    meta_data: dict

    _parameter_names: tuple = (
        "api_key_issuer_id",
        "api_key_id",
        "api_key_content",
        "output_directory",
        "changelog",
        "groups",
        "max_upload_attempts",
        "attempt_timeout",
    )

    def get_values(self) -> list:
        return [getattr(self, name) for name in self._parameter_names]

    def __init__(self) -> None:
        self.meta_data = {}
        type_hints = get_type_hints(UploadParameters)
        for name in self._parameter_names:
            self.meta_data[name] = {
                "source": ParameterSource.NONE,
                "type": type_hints[name]
            }

    def load(self) -> None:
        self._load_parameters_from_defaults()
        self._load_parameters_from_env()
        self._load_parameters_from_cli()

        unset_parameters = set(self._get_unset_parameter_names())
        set_parameters = set(self._parameter_names) - unset_parameters
        max_name_length = max(map(lambda s: len(s), set_parameters))
        print("Parameters found:")
        for name in set_parameters:
            print(f"  * {name:<{max_name_length}} (found in {self.meta_data[name]['source'].name})")

        if len(unset_parameters) > 0:
            message = f"Missing parameters: {', '.join(unset_parameters)}"
            pretty_print(f"<error>{message}</error>")
            raise KeyError(message)

    def _load_parameters_from_defaults(self) -> None:
        for parameter_name in self._parameter_names:
            if hasattr(self, parameter_name):
                self.meta_data[parameter_name]["source"] = ParameterSource.DEFAULTS

    def _load_parameters_from_env(self) -> None:
        for parameter_name in self._parameter_names:
            env_name = parameter_name.upper()
            if env_name in os.environ:
                self._try_set_parameter(parameter_name, input_cleaning.unescape(os.environ[env_name]), ParameterSource.ENV)

    def _load_parameters_from_cli(self) -> None:
        parser = argparse.ArgumentParser()
        for parameter_name in self._parameter_names:
            parser.add_argument("--" + parameter_name.replace("_", "-"))
        known, unknown = parser.parse_known_args()

        pretty_print(f"<warning>Got unknown command line args: {', '.join(unknown)}</warning>")

        input_cleaning.replace_hypens_with_underscore(known)
        for parameter_name in self._parameter_names:
            if parameter_name in known:
                self._try_set_parameter(parameter_name, getattr(known, parameter_name), ParameterSource.CLI)

    def _try_set_parameter(self, name: str, value, source: ParameterSource) -> bool:
        if value == None: return False

        try:
            value = cast_cli_arg(value, self.meta_data[name]["type"])
        except:
            return False

        setattr(self, name, value)
        self.meta_data[name]["source"] = source

        return True
    
    def _get_unset_parameter_names(self) -> list[str]:
        names = []
        for parameter_name in self._parameter_names:
            if self.meta_data[parameter_name]["source"] == ParameterSource.NONE:
                names.append(parameter_name)
        return names