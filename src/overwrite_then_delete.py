"""Utilities for best-effort secure overwrite and deletion of sensitive files."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterator


SECURE_DELETE_COMMANDS_BY_PLATFORM = {
    "darwin": [["srm", "-f", "{path}"]],
    "linux": [["shred", "--remove", "--zero", "{path}"]],
    "nt": [["sdelete", "-q", "-p", "1", "{path}"]],
}


def overwrite_then_delete(path: Path) -> None:
    """Overwrite a file with random bytes before deleting it."""
    fill_with_junk(path)


def fill_with_junk(path: Path) -> None:
    """Fill an existing file with random bytes matching its current size."""
    chars_to_write = _get_contents_length(path)
    with open(path, "r+b") as file:
        file.write(os.urandom(chars_to_write))
        file.flush()
        os.fsync(file.fileno())


def _get_contents_length(path: Path, default_length=1000) -> int:
    """Return file length in characters, or a fallback when the file is missing."""
    if not path.exists():
        return default_length
    with open(path, "r") as file:
        return len(file.read())


def delete(path: Path) -> None:
    """Delete a file using platform-specific secure tools, then fallback to unlink."""
    if not path.exists():
        return

    for command_template in _get_secure_delete_commands_for_current_platform():
        command = [part.format(path=str(path)) for part in command_template]
        if _try_run_command(command) and not path.exists():
            return

    path.unlink(missing_ok=True)


def _get_secure_delete_commands_for_current_platform() -> Iterator:
    """Yield secure-delete command templates for the current runtime platform."""
    current_platform = sys.platform
    for platform in SECURE_DELETE_COMMANDS_BY_PLATFORM.keys():
        if current_platform.startswith(platform):
            yield from SECURE_DELETE_COMMANDS_BY_PLATFORM[platform]


def _try_run_command(cmd: list[str]) -> bool:
    """Run a command quietly when available and report whether it succeeded."""
    if shutil.which(cmd[0]) is None:
        return False

    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0
