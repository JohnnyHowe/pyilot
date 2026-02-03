"""
Environment variable accessor for Upload to TestFlight.
Loads and verifies required environment variables exist (not content).
See # region Vars for all variables loaded. (Some are optional - but will always have a default value).
"""
import os
from pathlib import Path
from typing import Optional
# TODO find better solution to this
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pretty_print import *


# region Vars 
APP_STORE_CONNECT_API_KEY_ISSUER_ID: str
APP_STORE_CONNECT_API_KEY_KEY_ID: str
APP_STORE_CONNECT_API_KEY_CONTENT: str
OUTPUT_DIRECTORY: Path
GROUPS: Optional[str]
MAX_UPLOAD_ATTEMPTS: int
TIMEOUT_PER_ATTEMPT: int


# region Loading
# Defaults: type: string, required: True, sensitive: True
_ALL_VARIABLES = {
    "APP_STORE_CONNECT_API_KEY_ISSUER_ID": {},
    "APP_STORE_CONNECT_API_KEY_KEY_ID": {},
    "APP_STORE_CONNECT_API_KEY_CONTENT": {},
    "GROUPS": {"required": False, "sensitive": False, "default": None},
    "OUTPUT_DIRECTORY": {"type": Path, "sensitive": False},
    "MAX_UPLOAD_ATTEMPTS": {"type": int, "required": False, "sensitive": False, "default": 10},
    "TIMEOUT_PER_ATTEMPT": {"type": int, "required": False, "sensitive": False, "default": 60 * 5},
}

_NO_DOTENV_ERROR_MESSAGE="""Missing dependency: python-dotenv.
This can be ignored if you're not using a .env file.
If you are using .env, install dotenv with `pip install python-dotenv` (maybe python3 - check your system)"""

_SENSITIVE_VARIABLE_PRINT_VALUE="[redacted]"


def _load():
    _populate_defaults()

    # Load as much without dotenv
    not_found = _try_load_env("system")
    not_found_and_required = list(filter(lambda var_name: _ALL_VARIABLES[var_name].get("required", True), not_found))

    # quit early if we have everything we need
    if len(not_found_and_required) == 0:
        pretty_print(f"Found all required environent variables!\n{_get_printable_str()}", color=SUCCESS)
        return

    # import dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError as error:
        pretty_print(_NO_DOTENV_ERROR_MESSAGE, color=ERROR)
        not_found_variables_display = "\n".join(map(lambda s: "  - " + s, not_found_and_required))
        pretty_print(f"Could not find the following environment variables:\n{not_found_variables_display}", color=ERROR)
        raise error

    # load vars from dotenv
    not_found = _try_load_env(".env")
    not_found_and_required = list(filter(lambda var_name: _ALL_VARIABLES[var_name].get("required", True), not_found))

    # quit early if we have everything we need
    if len(not_found_and_required) == 0:
        pretty_print(f"Found all required environent variables with python-dotenv\n{_get_printable_str()}", color=SUCCESS)
        return

    not_found_variables_display = "\n".join(map(lambda s: "  - " + s, not_found_and_required))
    error_message = f"Could not find the following environment variables!\n{not_found_variables_display}"
    pretty_print(error_message, color=ERROR)
    raise ValueError(error_message)


def _populate_defaults():
    for var_name, options in _ALL_VARIABLES.items():
        if not "default" in options:
            continue
        set_env_var(var_name, options["default"])
        options["found_in"] = "defaults"
        

def _get_printable_str() -> str:
    result = ""
    for var_name, options in _ALL_VARIABLES.items():

        result += f"\n  - {var_name}="

        if options.get("sensitive", True):
            result += _SENSITIVE_VARIABLE_PRINT_VALUE
        else:
            result += str(get_env_var(var_name))
        
        result += f" (found in {options.get('found_in', 'unknown')})"

    return result.strip("\n")


def _try_load_env(found_in: str) -> list:
    """ Returns names of variables that could not be set. """
    not_found = []
    for var_name, options in _ALL_VARIABLES.items():
        if var_name in os.environ:
            value = os.environ[var_name]
            if "type" in options:
                value = options["type"](value)
            set_env_var(var_name, value)
            options["found_in"] = found_in
        else:
            not_found.append(var_name)
    return not_found


def get_env_var(name: str) -> object:
    return globals()[name]


def set_env_var(name: str, value) -> None:
    globals()[name] = value


_load()