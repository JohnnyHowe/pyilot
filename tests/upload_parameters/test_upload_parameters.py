from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ucb_to_testflight.upload_parameters import ParameterSource, UploadParameters


class UploadParametersTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env_patch = patch.dict(os.environ, {}, clear=True)
        self._argv_patch = patch("sys.argv", ["test"])
        self._env_patch.start()
        self._argv_patch.start()
        self.addCleanup(self._env_patch.stop)
        self.addCleanup(self._argv_patch.stop)

    def test_load_reads_required_values_from_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            os.environ.update(
                {
                    "APP_STORE_CONNECT_API_KEY_ISSUER_ID": "issuer",
                    "APP_STORE_CONNECT_API_KEY_ID": "key",
                    "APP_STORE_CONNECT_API_KEY_CONTENT": "private-key-content",
                    "OUTPUT_DIRECTORY": str(root),
                    "CHANGELOG_PATH": str(root / "CHANGELOG.txt"),
                }
            )

            parameters = UploadParameters()
            parameters.load()

            self.assertEqual(parameters.app_store_connect_api_key_issuer_id, "issuer")
            self.assertEqual(parameters.app_store_connect_api_key_id, "key")
            self.assertEqual(parameters.app_store_connect_api_key_content, "private-key-content")
            self.assertEqual(parameters.output_directory, root)
            self.assertEqual(parameters.changelog_path, root / "CHANGELOG.txt")
            self.assertEqual(parameters.max_upload_attempts, 10)
            self.assertEqual(parameters.attempt_timeout, 600)
            self.assertEqual(parameters.meta_data["app_store_connect_api_key_id"]["source"], ParameterSource.ENV)
            self.assertEqual(parameters.meta_data["max_upload_attempts"]["source"], ParameterSource.DEFAULTS)

    def test_cli_overrides_environment_and_casts_int_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            os.environ.update(
                {
                    "APP_STORE_CONNECT_API_KEY_ISSUER_ID": "env-issuer",
                    "APP_STORE_CONNECT_API_KEY_ID": "env-key",
                    "APP_STORE_CONNECT_API_KEY_CONTENT": "env-content",
                    "OUTPUT_DIRECTORY": str(root),
                    "CHANGELOG_PATH": str(root / "notes.txt"),
                    "MAX_UPLOAD_ATTEMPTS": "3",
                    "ATTEMPT_TIMEOUT": "60",
                }
            )

            with patch(
                "sys.argv",
                [
                    "test",
                    "--max-upload-attempts",
                    "9",
                    "--attempt-timeout",
                    "120",
                    "--app-store-connect-api-key-id",
                    "cli-key",
                ],
            ):
                parameters = UploadParameters()
                parameters.load()

            self.assertEqual(parameters.app_store_connect_api_key_id, "cli-key")
            self.assertEqual(parameters.max_upload_attempts, 9)
            self.assertEqual(parameters.attempt_timeout, 120)
            self.assertEqual(parameters.meta_data["app_store_connect_api_key_id"]["source"], ParameterSource.CLI)
            self.assertEqual(parameters.meta_data["max_upload_attempts"]["source"], ParameterSource.CLI)
            self.assertEqual(parameters.meta_data["attempt_timeout"]["source"], ParameterSource.CLI)

    def test_missing_required_values_raises_key_error(self) -> None:
        parameters = UploadParameters()

        with self.assertRaises(KeyError) as ctx:
            parameters.load()

        self.assertIn("app_store_connect_api_key_issuer_id", str(ctx.exception))
        self.assertIn("app_store_connect_api_key_id", str(ctx.exception))
        self.assertIn("app_store_connect_api_key_content", str(ctx.exception))
        self.assertIn("output_directory", str(ctx.exception))
        self.assertIn("changelog_path", str(ctx.exception))

    def test_get_values_returns_values_in_parameter_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            os.environ.update(
                {
                    "APP_STORE_CONNECT_API_KEY_ISSUER_ID": "issuer",
                    "APP_STORE_CONNECT_API_KEY_ID": "key",
                    "APP_STORE_CONNECT_API_KEY_CONTENT": "content",
                    "OUTPUT_DIRECTORY": str(root),
                    "CHANGELOG_PATH": str(root / "notes.txt"),
                    "GROUPS": "alpha,beta",
                    "MAX_UPLOAD_ATTEMPTS": "7",
                    "ATTEMPT_TIMEOUT": "90",
                }
            )

            parameters = UploadParameters()
            parameters.load()
            values = parameters.get_values()

            self.assertEqual(values[0], "issuer")
            self.assertEqual(values[1], "key")
            self.assertEqual(values[2], "content")
            self.assertEqual(values[3], root)
            self.assertEqual(values[4], root / "notes.txt")
            self.assertEqual(values[6], 7)
            self.assertEqual(values[7], 90)


if __name__ == "__main__":
    unittest.main()
