from .upload_configuration import UploadConfiguration
from command_utility import *
from pretty_print import *


class TestflightUploader:
    verbose: bool
    last_altool_output = []
    configuration: UploadConfiguration
    command: Command

    _print_prefix: str = "[TestFlightUploader]"

    def __init__(self, configuration: UploadConfiguration) -> None:
        self.configuration = configuration
        self._create_command()

    def _create_command(self):
        self.command = Command()
        self.command.executable = "fastlane"
        self.command.subcommands = ["pilot", "upload"]
        self.command.add_flag_and_value("-i", str(self.configuration.ipa_path))
        self.command.add_flag_and_value("--api-key-path", str(self.configuration.app_store_key_path))
        self.command.add_flag_and_value("--changelog", f"\"{self._read_changelog()}\"")
        if self._should_include_groups():
            assert self.configuration.groups
            self.command.add_flag_and_value("--groups", self.configuration.groups)
        self.command.add_flag("--verbose")

    def _should_include_groups(self):
        if not isinstance(self.configuration.groups, str):
            return False
        stripped = self.configuration.groups.strip()
        if stripped == "":
            return False
        return True

    def upload(self) -> bool:
        pretty_print(f"{self._print_prefix} running following command\n{self.command.to_str(newlines=True)}")
        for attempt_number in range(self.configuration.max_upload_attempts):
            pretty_print(f"{self._print_prefix} Starting attempt {attempt_number + 1} of {self.configuration.max_upload_attempts}")
            command_output = self._try_upload()
            if command_output.success:
                return True
        pretty_print(f"{self._print_prefix} Out of upload attempts!", color=ERROR)
        return False
            
    def _try_upload(self) -> CommandOutput:
        runner = CommandRunner(self.command)
        runner.timeout_seconds = self.configuration.timeout_per_attempt_seconds
        pretty_print(f"{self._print_prefix} TODO write command runner output parser", color=TODO)
        runner.run()
        return runner.output

    def _read_changelog(self) -> str:
        with open(self.configuration.changelog_path, "r") as file:
            return file.read()