from typing import Iterator, Optional
from python_command_runner import OutputLine, OutputSource
from python_pretty_print import pretty_print


_error_checkers = []

class Error:
    exception: Exception
    target_lines: list[OutputLine]
    hint: Optional[str]

    def __init__(self, exception: Exception, hint: Optional[str] = None, target_lines: list[OutputLine] = []) -> None:
        self.exception = exception
        self.target_lines = target_lines
        self.hint = hint

    def __str__(self) -> str:
        text = f"{type(self.exception).__name__}: {self.exception}"
        if self.hint is not None:
            text += f"\nHint: {self.hint}"
        return text


class ExceptionCollection(Exception):
    exceptions: list[Exception]

    def __init__(self, exceptions: list[Exception] = []) -> None:
        self.exceptions = exceptions
        super().__init__()

    @property
    def message(self) -> str:
        """Generate a summary message on the fly"""
        lines = [f"Exception collection of {len(self.exceptions)} exceptions"]
        for exception in self.exceptions:
            lines.append(f"{exception}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.message

    def __iter__(self):
        return iter(self.exceptions)


def get_errors(success_from_exit_code: bool, lines: list[OutputLine]) -> list[Error]:
    errors = list(_get_errors_iterator(lines))
    if len(errors) == 0 and not success_from_exit_code:
        lines = [line for line in lines if line.source == OutputSource.STDERR and "error" in line.text.lower()]
        errors.append(Error(Exception("Unknown. Probably something to do with the following."), target_lines=lines))
    return errors


def _get_errors_iterator(lines: list[OutputLine]) -> Iterator[Error]:
    for check in _error_checkers:
        for error in check(lines):
            yield error


def print_errors(errors: list[Error]) -> None:
    if len(errors) == 0:
        return

    pretty_print(f"<error>\n{'Found errors in logs! ':=<100}</error>")
    for error in errors:
        print()
        _log_error(error)

    pretty_print(f"<error>\n{'':=<100}\n</error>")


def raise_errors(errors: list[Error]) -> None:
    raise ExceptionCollection(list(map(lambda error: error.exception, errors)))


def _log_error(error: Error) -> None:
    pretty_print(f"<error>{error}</error>")
    for line in error.target_lines:
        pretty_print(f"<error> -> [{line.index}] {line.text}</error>")


# ==================================================================================================
# region Error Checkers 
# ==================================================================================================

def _check_invalid_curve_name_error(lines: list[OutputLine]) -> Iterator[Error]:
    for line in lines:
        if line.source != OutputSource.STDERR:
            continue
        if "[!] invalid curve name" in line.text.lower():
            error = Error(Exception("API key check failed! (Found \"[!] invalid curve name\" in logs)"))
            error.target_lines = [line]
            error.hint = "Double check your api key values."
            yield error

_error_checkers.append(_check_invalid_curve_name_error)


def _check_version_number_error(lines: list[OutputLine]) -> Iterator[Error]:
    error_lines = []
    for line in lines:
        if line.source != OutputSource.STDERR:
            continue
        if not "The provided entity includes an attribute with a value that has already been used" in line.text:
            continue
        error_lines.append(line)
    if len(error_lines) > 0:
        error = Error(Exception("Bundle version has already been used!"))
        error.target_lines = error_lines
        yield error

_error_checkers.append(_check_version_number_error)