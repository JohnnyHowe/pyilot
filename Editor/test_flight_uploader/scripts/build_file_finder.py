"""
Looks for the build file in the environment variable OUTPUT_DIRECTORY.

Made for Unity Cloud Build .ipa and .aab files.
Executable path is OUTPUT_DIRECTORY/executable_name.type for UCB.
PS. UCB does expose the full path but it's in an API that I can't be bothered touching (https://build-api.cloud.unity3d.com/docs).
"""
import argparse
from pathlib import Path
from typing import Iterator
from env_accessor import *
# TODO find better solution to this
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pretty_print import *

class BuildFileFinder:
    file_extension: str
    file_path: Path

    def __init__(self, file_extension: str):
        self._set_file_extension(file_extension)
        self._find_and_set_file()

    def _set_file_extension(self, file_extension: str) -> None:
        """ Set self.file_extension as a lowercase version of file_extension and add "." prefix if required. """
        self.file_extension = file_extension.lower()
        if not self.file_extension.startswith("."):
            self.file_extension = "." + file_extension

    def _find_and_set_file(self) -> None:
        self.file_path = self._find_file()
        if self.file_path is None:
            raise FileNotFoundError(f"No {self.file_extension} found.")

    def _find_file(self) -> Path:
        for searcher in [self._search_output_directory]:    # If you want to search more places, add functions to this list
            path = searcher()
            if path: 
                return path

        raise FileNotFoundError(f"No {self.file_extension} file found!")

    def _search_output_directory(self):
        """
        Get file at $OUTPUT_DIRECTORY/build_name.type
        If $OUTPUT_DIRECTORY doesn't exist or the file doesn't, return None
        """
        if not OUTPUT_DIRECTORY.exists():
            raise_pretty_exception(FileNotFoundError, BuildFileFinder._get_log_text(f"$OUTPUT_DIRECTORY ({get_pretty_path_string(OUTPUT_DIRECTORY)}) doesn't exist!"))
            return None
        return self._choose_file(list(self._search_path(OUTPUT_DIRECTORY)))

    def _search_path(self, root: Path, recursive=False) -> Iterator:
        for file_name in os.listdir(root):
            file_path = Path(os.path.join(root, file_name))

            if file_path.is_dir() and recursive:
                yield from self._search_path(file_path, recursive)

            if not file_path.is_file(): continue
            if not file_path.suffix.lower() == self.file_extension: continue

            yield file_path

    def _choose_file(self, paths: list):
        if len(paths) == 0:
            self._log(f"Found 0 {self.file_extension} files")
            return None

        if len(paths) == 1:
            self._log(f"Found 1 {self.file_extension} file: {paths[0]}", SUCCESS)
            return paths[0]

        self._log(f"Found {len(paths)} {self.file_extension} files:", WARNING)
        for file_path in paths:
            self._log(f"  - {file_path}")

        self._log("TODO: choose smarter. Taking first...", TODO)
        return paths[0]

    def _log(self, text: str, color = REGULAR):
        pretty_print(BuildFileFinder._get_log_text(text), color=color)

    @staticmethod
    def _get_log_text(text: str) -> str:
        return "[BuildFileFinder] " + text


def find_build_file_path(extension: str) -> Path:
    return BuildFileFinder(extension).file_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "extension",
        help="File extension to search for (e.g. .aab or .ipa)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()
    print(find_build_file_path(args.extension))
