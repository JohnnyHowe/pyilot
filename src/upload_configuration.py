"""
Contains all the information needed to upload a build to TestFlight.
Is one step more abstract than the env_accessor (uses it).
Verifies that all required information is present and valid.
"""
import json
from pathlib import Path
from typing import Optional
from testflight_uploader.build_file_finder import find_build_file_path
# TODO find better solution to this
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pretty_print import *
from env_accessor import *


class UploadConfiguration:
    # from env
    groups: Optional[str]
    max_upload_attempts: int
    timeout_per_attempt_seconds: int
    # derived
    changelog_path: Path
    ipa_path: Path
    app_store_key_path: Path

    # defaults
    _max_upload_attempts_fallback = 10
    _max_timeout_per_attempt_seconds = 10

    # non config
    _print_header = "[UploadConfiguration]"

    def __init__(self, api_key_path: Path):
        self.app_store_key_path = api_key_path
        self._populate()
        self._try_repair()
        self.verify()
        pretty_print(f"{self._print_header} Created upload configuration\n{self}", color=SUCCESS)

    def _populate(self):
        self.groups = GROUPS
        self.max_upload_attempts = MAX_UPLOAD_ATTEMPTS
        self.timeout_per_attempt_seconds = ATTEMPT_TIMEOUT

        self.ipa_path = find_build_file_path(".ipa")

        pretty_print(f"{self._print_header} TODO expose changelog. Currently it's hardcoded to Assets/Editor/CICD/newest_changelog.txt.", color=TODO)
        self.changelog_path = Path("Assets/Editor/CICD/newest_changelog.txt")

    def _try_repair(self) -> None:
        """ Tries to fix invalid configuration values."""
        if self.max_upload_attempts <= 0:
            pretty_print(f"{self._print_header} Invalid MAX_UPLOAD_ATTEMPTS value! Found {self.max_upload_attempts}, falling back to {self._max_upload_attempts_fallback}", color=WARNING)
            self.max_upload_attempts = self._max_upload_attempts_fallback
        if self._max_timeout_per_attempt_seconds <= 0:
            pretty_print(f"{self._print_header} Invalid TIMEROUT_PER_ATTEMPT value! Found {self.timeout_per_attempt_seconds}, falling back to {self._max_timeout_per_attempt_seconds}", color=WARNING)
            self.max_upload_attempts = self._max_upload_attempts_fallback

    def verify(self) -> None:
        """ Verifies that all required configuration values are valid. Raises on invalid values. """
        self._verify_is_file(self.app_store_key_path, "App Store Connect key")
        self._verify_app_store_key_format()
        self._verify_is_file(self.changelog_path, "changelog")
        self._verify_is_file(self.ipa_path, "build file")

    def _verify_is_file(self, path: Path, data_name: str):
        if not self.app_store_key_path.exists():
            raise FileNotFoundError(f"Error loading {data_name}! Nothing found at {path}")

        if not self.app_store_key_path.is_file():
            raise FileNotFoundError(f"Error loading {data_name}. Item at {path} is not a file!")

    def _verify_app_store_key_format(self):
        with open(self.app_store_key_path, "r") as file:
            self._verify_app_store_key_content(file.read())

    def _verify_app_store_key_content(self, content: str):
        data = json.loads(content)
        self._verify_dictionary_value_not_env_reference("key_id", data, str(self.app_store_key_path))
        self._verify_dictionary_value_not_env_reference("issuer_id", data, str(self.app_store_key_path))
        self._verify_dictionary_value_not_env_reference("key", data, str(self.app_store_key_path))
        
    def _verify_dictionary_value_not_env_reference(self, key: str, data: dict, data_name: str):
        if not key in data:
            raise KeyError(f"\"{key}\" not found in \"{data_name}\"")
        key_id = data[key]
        if key_id.startswith("$"):
            raise ValueError(f"{data_name} \"{key}\" invalid. Got \"{key_id}\"")

    def __str__(self) -> str:
        indent = "\t"

        result = "{\n"

        for item in ["ipa_path", "changelog_path", "app_store_key_path", "max_upload_attempts", "timeout_per_attempt_seconds", "groups"]:
            if item == "":
                result += "\n"
                continue
            result += f"{indent}{item}: {getattr(self, item)}\n"

        result += "}"

        return result