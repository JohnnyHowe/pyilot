from pathlib import Path

from build_file_finder import BuildFileFinder
from api_key import *
from fastlane_pilot_output_log_error_checker import get_errors, print_errors, raise_errors
from python_command_line_helpers import command_building
from python_pretty_print import pretty_print
from python_command_runner import *


def upload_to_testflight(
	api_key_issuer_id: str,
	api_key_id: str,
	api_key_content: str,
	output_directory: Path,
	changelog: str,
	groups: list[str] = [],
	max_upload_attempts: int = 10,
	attempt_timeout_seconds: int = 600,
):
	ipa_path = BuildFileFinder(output_directory, ".ipa").file_path
	api_key = APIKey(api_key_issuer_id, api_key_id, api_key_content)
	print(api_key._file_path)

	command = _build_command(ipa_path, api_key.file_path, changelog, groups)

	_run_attempt(command, attempt_timeout_seconds)


def _build_command(
	ipa_path: Path,
	api_key_path: Path,
	changelog: str,
	groups: list[str],
) -> list[str]:
	command = ["fastlane", "pilot", "upload", "--verbose"]
	command += ["-i", ipa_path]
	command += ["--api-key-path", api_key_path]
	command += ["--changelog", changelog]

	if len(groups) > 0:
		command += ["--groups", ",".join(groups)]

	command_building.resolve_paths(command)
	return command


def _run_attempt(command: list[str], timeout_seconds: int, print_log_stream: bool = False) -> None:
	"""Raises exceptions on failure. No exception = success."""

	header = f"Showing {'all' if print_log_stream else 'filtered'} logs "
	print(f"\n{header:=<100}\n")

	success, lines = _run_attempt_command(command, timeout_seconds, print_log_stream)
	errors = get_errors(success, lines)

	if len(errors) > 0:
		if not print_log_stream:
			pretty_print(f"<error>\n{'Found errors! Showing all logs ':=<100}\n</error>")
			for line in lines:
				color = "error" if line.source == OutputSource.STDERR else "dull"
				pretty_print(f"[{line.index}]<{color}>[{line.source}]</{color}> {line.text}")

		if success:
			print()
			print("Something peculiar has happened. fastlane indicated success, but there seem to be errors.")

		print_errors(errors)
		# raise_errors(errors)
		quit()


def _run_attempt_command(command: list[str], timeout_seconds: int, print_log_stream: bool = False) -> tuple[bool, list[OutputLine]]:
	""" returns (success, lines) """
	lines: list[OutputLine] = []
	generator = run_command(command, timeout_seconds=timeout_seconds)
	try:
		while True:
			output_line = next(generator)
			lines.append(output_line)
			if print_log_stream or _is_useful_status_log(output_line):
				print(output_line.text)
	except StopIteration as exception:
		print(exception.value)
		return (exception.value == 0, lines)


def _is_useful_status_log(line: OutputLine) -> bool:
	contains_checks = [
		"Ready to upload new build to TestFlight",
		"Going to upload updated app to App Store Connect",
	]
	for contains_check in contains_checks:
		if contains_check in line.text:
			return True

	return False