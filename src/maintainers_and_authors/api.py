from typing import Iterable

from . import core

def version_tuple_from_str(s: str) -> tuple:
    return core._version_tuple_from_str(s)

def email_addresses(
    project_names: Iterable[str],
    min_python_version: tuple = (),
    ) -> dict[str, set[str]]:
    return core._email_addresses(project_names, min_python_version)