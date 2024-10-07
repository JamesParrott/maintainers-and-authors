import collections
import sys
from typing import Iterable, Iterator

import requests


def _version_tuple_from_str(s: str):
    return tuple(int(c) for c in s.split('.'))


def _python_version_constraints(meta_data: dict[str, str]) -> Iterator[tuple[str, str]]:
    
    if 'requires_python' in meta_data:

        for clause in meta_data['requires_python'].split(','):

            clause = clause.strip().replace(' ','')

            if clause.startswith('==='):
                yield '===', clause[3:]
                continue

            if clause[1] != '=':
                yield clause[0], clause[1:]
                continue

            assert clause[0] in '<~!=>', f'Non-compliant clause: {clause} in project: {meta_data["name"]}'

            yield clause[:2], clause[2:]


def _python_version_classifiers(meta_data: dict[str, str]) -> Iterator[str]:
    if 'classifier' in meta_data:
        older_supported_versions = []
        for entry in meta_data['classifier']:
            if not entry.startswith('Programming Language :: Python ::'):
                continue
            yield entry.removeprefix('Programming Language :: Python ::').partition('::')[0].strip()




def _email_addresses(
    project_names: Iterable[str],
    min_python_version: tuple = (),
    ) -> dict[str, set[str]]:



    def excludes_unsupported_versions(
        comparison_operator: str,
        version_identifier: tuple,
        ) -> bool:
        
        # Misses '>' highest version  below min_python_version
        if comparison_operator in {'>',
                                   '>=',
                                   '==',  #Could miss hard negative. Wild cards not processed.
                                   '===',
                                   '~=',  # Could miss hard negative.  
                                   } and _version_tuple_from_str(version_identifier) >= min_python_version:
            return True

        # Misses an exhaustive list of version exclusions of earlier versions with '!='


        return False

    # Use a set in case author and maintainer fields are both set for the same project
    projects = collections.defaultdict(set)

    # print('Processing projects: ', end='')

    for project_name in project_names:

        project_name = project_name.rstrip()

        # print(f'{project_name}, ', end='', flush=True)
        response = requests.get(f'https://www.wheelodex.org/json/projects/{project_name}/data')

        response.raise_for_status()

        meta_data = response.json()['data']['dist_info']['metadata']

        if any(excludes_unsupported_versions(comparison_operator, version_identifier)
               for comparison_operator, version_identifier in _python_version_constraints(meta_data)):
            continue

        classifiers = list(_python_version_classifiers(meta_data))

        if classifiers and not any(_version_tuple_from_str(version_identifier) < min_python_version
                                   for version_identifier in classifiers):
            continue


        # Don't str.casefold email addresses.  
        # If someone specified a ß and not an 'ss', preserve their choice.
        author = meta_data.get('author_email','')
        maintainer = meta_data.get('maintainer_email','').lower()

        if author:
            projects[author].add(project_name)
        if maintainer:
            projects[maintainer].add(project_name)


    return projects
