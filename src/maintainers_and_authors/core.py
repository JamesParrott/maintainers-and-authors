import collections
import email.utils
import itertools
import sys
from typing import Iterable, Iterator

import requests
from tqdm import tqdm


def _version_tuple_from_str(s: str) -> tuple:
    return tuple(int(c) for c in s.split('.'))


def _parse_mail_boxes(mail_boxes: str) -> Iterator[tuple[str, str]]:
    while mail_boxes:
        name, email_ = email.utils.parseaddr(mail_boxes)

        if (name, email_) == ('', ''):
            break

        if email_.endswith('.noreply.github.com'):
            continue

        yield name, email_

        mail_boxes = (mail_boxes.partition(f'<{email_}>')[2]
                                .lstrip()
                                .removeprefix(',')
        )




def _email_addresses(
    project_names: Iterable[str],
    min_python_version: tuple = (),
    ) -> dict[str, dict[str, dict]]:



    projects = collections.defaultdict(dict)

    # print('Processing projects: ', end='')

    for project_name in tqdm(project_names):

        project_name = project_name.rstrip()

        # print(f'{project_name}, ', end='', flush=True)
        response = requests.get(f'https://www.wheelodex.org/json/projects/{project_name}/data')

        response.raise_for_status()

        meta_data = response.json()['data']['dist_info']['metadata']


        names, emails = [], []
        for name, email_ in itertools.chain(
                    # Use boolean "or" instead of a default in .get, e.g. .get(key, '') 
                    # as it is possible that meta_data['author_email'] is None.
                    _parse_mail_boxes(meta_data.get('maintainer_email') or ''),
                    _parse_mail_boxes(meta_data.get('author_email') or ''),
                    ):
            names.append(name)
            emails.append(email_)

        if names and emails:
            project_data = dict(
                meta_data = meta_data,
                # duplicate emails in the key, to preserve ordering for correspondence with names
                maintainers_and_authors = (emails, names),
            )
            
            projects[frozenset(emails)][project_name] = project_data



    return projects
