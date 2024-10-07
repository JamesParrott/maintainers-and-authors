from typing import Iterable

from .core import _email_addresses


def email_addresses(
    project_names: Iterable[str],
    min_python_version: tuple = (),
    ) -> dict[str, set[str]]:
    return _email_addresses(project_names, min_python_version)