"""UCB adapter that delegates TestFlight upload execution to pyliot."""
from pathlib import Path

from pyliot.upload_to_testflight import upload_to_testflight as pyliot_upload_to_testflight
from .build_file_finder import BuildFileFinder


def upload_to_testflight(
	app_store_connect_api_key_issuer_id: str,
	app_store_connect_api_key_id: str,
	app_store_connect_api_key_content: str,
	output_directory: Path,
	changelog_path: Path,
	groups: list[str] = [],
	max_upload_attempts: int = 10,
	attempt_timeout_seconds: int = 600,
):
	ipa_path = BuildFileFinder(output_directory, ".ipa").file_path

	with open(changelog_path, "r") as file:
		changelog = file.read()

	pyliot_upload_to_testflight(
		app_store_connect_api_key_issuer_id=app_store_connect_api_key_issuer_id,
		app_store_connect_api_key_id=app_store_connect_api_key_id,
		app_store_connect_api_key_content=app_store_connect_api_key_content,
		ipa_path=ipa_path,
		changelog=changelog,
		groups=groups,
		max_upload_attempts=max_upload_attempts,
		attempt_timeout_seconds=attempt_timeout_seconds,
	)
