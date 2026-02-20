from __future__ import annotations

import importlib
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


class UploadToTestFlightTests(unittest.TestCase):
    def _import_module_with_stubbed_pyliot(self):
        upload_mock = Mock()
        pyliot_pkg = types.ModuleType("pyliot")
        pyliot_upload_module = types.ModuleType("pyliot.upload_to_test_flight")
        pyliot_upload_module.upload_to_testflight = upload_mock
        pyliot_pkg.upload_to_test_flight = pyliot_upload_module

        patched_modules = {
            "pyliot": pyliot_pkg,
            "pyliot.upload_to_test_flight": pyliot_upload_module,
        }

        with patch.dict(sys.modules, patched_modules, clear=False):
            sys.modules.pop("ucb_to_testflight.upload_to_test_flight", None)
            module = importlib.import_module("ucb_to_testflight.upload_to_test_flight")

        return module, upload_mock

    def test_upload_delegates_to_pyliot_with_changelog_contents(self) -> None:
        module, pyliot_upload_mock = self._import_module_with_stubbed_pyliot()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            changelog_path = root / "CHANGELOG.txt"
            changelog_path.write_text("Release notes", encoding="utf-8")
            ipa_path = root / "build.ipa"
            ipa_path.write_text("binary", encoding="utf-8")

            with patch.object(module, "BuildFileFinder") as finder_cls:
                finder_cls.return_value.file_path = ipa_path

                module.upload_to_testflight(
                    app_store_connect_api_key_issuer_id="issuer-id",
                    app_store_connect_api_key_id="key-id",
                    app_store_connect_api_key_content="key-content",
                    output_directory=root,
                    changelog_path=changelog_path,
                    groups=["group-a", "group-b"],
                    max_upload_attempts=5,
                    attempt_timeout_seconds=123,
                )

        finder_cls.assert_called_once_with(root, ".ipa")
        pyliot_upload_mock.assert_called_once_with(
            api_key_issuer_id="issuer-id",
            api_key_id="key-id",
            api_key_content="key-content",
            ipa_path=ipa_path,
            changelog="Release notes",
            groups=["group-a", "group-b"],
            max_upload_attempts=5,
            attempt_timeout_seconds=123,
        )


if __name__ == "__main__":
    unittest.main()
