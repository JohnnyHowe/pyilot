from pathlib import Path
from build_file_finder import BuildFileFinder
from api_key import *
from python_command_line_helpers import command_building
from python_pretty_print import pretty_print
from python_command_runner import *
from upload_attempt import run_attempt


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

	command = _build_command(ipa_path, api_key.file_path, changelog, groups)

	for i in range(max_upload_attempts):
		try:
			run_attempt(command, attempt_timeout_seconds)
			break
		except:
			pretty_print(f"<warning>Failed upload attempt {i + 1} / {max_upload_attempts}</warning>")


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

