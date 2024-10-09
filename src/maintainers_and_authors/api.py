import sys

from . import core


def version_tuple_from_str(s: str) -> tuple:
    return core._version_tuple_from_str(s)

def email_addresses(
    min_python_version: tuple = (),
    ) -> dict[str, set[str]]:
    return core._email_addresses(sys.stdin, min_python_version)
