import atexit
import json
from pathlib import Path
from overwrite_then_delete import overwrite_then_delete as delete_file


class APIKey:
    """Wraps the contents, creation of, and destruction of the App Store Connect key file."""
    _api_key_issuer_id: str
    _api_key_id: str
    _api_key_content: str
    _file_path: Path

    def __init__(
        self,
        api_key_issuer_id: str,
        api_key_id: str,
        api_key_content: str,
        file_path: Path = Path("AppStoreConnectKey.json"),
    ) -> None:
        self._api_key_issuer_id = api_key_issuer_id
        self._api_key_id = api_key_id
        self._api_key_content = api_key_content
        self._file_path = file_path
        self._create_file()

        file_path_copy = self._file_path
        atexit.register(lambda: delete_file(file_path_copy))

    @property
    def file_path(self) -> Path:
        return self._file_path

    def delete_file(self) -> None:
        delete_file(self._file_path)

    def _create_file(self):
        with open(self._file_path, "w") as file:
            file.write(self._as_str())

    def _as_str(self) -> str:
        return json.dumps(self._as_dict(), indent="\t")

    def _as_dict(self) -> dict:
        return {
            "key_id": self._api_key_id,
            "issuer_id": self._api_key_issuer_id,
            "key": self._api_key_content,
        }
