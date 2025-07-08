import collections
import email.utils
import itertools
from typing import Iterable, Iterator

import requests


def _version_tuple_from_str(s: str) -> tuple:
    return tuple(int(c) for c in s.split("."))


def _parse_mail_boxes(mail_boxes: str) -> Iterator[tuple[str, str]]:
    while mail_boxes:
        # CVE-2023-27043 was found in email.utils.parseaddr, which
        # was fixed by making a breaking change to the old insecure behaviour
        # in multiple patch versions of Python 3.9, ..., 3.13,
        # that would be laborious and ugly to enumerate.
        try:
            name, email_ = email.utils.parseaddr(mail_boxes, strict=False)
        except TypeError:
            name, email_ = email.utils.parseaddr(mail_boxes)

        if (name, email_) == ("", ""):
            break

        if not email_.endswith(".noreply.github.com"):
            yield name, email_

        mail_boxes = mail_boxes.partition(f"<{email_}>")[2].lstrip().removeprefix(",")


def _email_addresses(
    project_names: Iterable[str],
    min_python_version: tuple = (),
) -> dict[frozenset[str], dict[str, dict]]:
    projects = collections.defaultdict(dict)

    for project_name in project_names:
        project_name = project_name.rstrip()

        if not project_name:
            continue

        url = f"https://www.pypi.org/pypi/{project_name}/json"

        # response = requests.get(f'https://www.wheelodex.org/json/projects/{project_name}/data')
        response = requests.get(url)

        response.raise_for_status()

        # meta_data = response.json()['data']['dist_info']['metadata']
        meta_data = response.json()["info"]

        names, emails = [], []
        for name, email_ in itertools.chain(
            # Use boolean "or" instead of a default in .get, e.g. .get(key, '')
            # as it is possible that meta_data['author_email'] is None.
            _parse_mail_boxes(meta_data.get("maintainer_email") or ""),
            _parse_mail_boxes(meta_data.get("author_email") or ""),
        ):
            names.append(name)
            emails.append(email_)

        if names and emails:
            project_data = dict(
                meta_data=meta_data,
                # duplicate emails in the key, to preserve ordering for correspondence with names
                maintainers_and_authors=(emails, names),
            )

            projects[frozenset(emails)][project_name] = project_data

    return projects
