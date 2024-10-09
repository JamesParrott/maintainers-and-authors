import collections
import sys
from typing import Iterable, Iterator

import requests


def _version_tuple_from_str(s: str) -> tuple:
    return tuple(int(c) for c in s.split('.'))


def _python_version_clauses(meta_data: dict[str, str]) -> Iterator[tuple[str, str]]:
    
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
    ) -> dict[str, dict[str, dict]]:



    def excludes_unsupported_versions(
        comparison_operator: str,
        version_identifier: tuple,
        ) -> bool:
        
        
        if comparison_operator in {'>', # Misses '>' highest released version  below min_python_version, 
                                        # e.g. > 3.1.9999999 would work just fine with >= 3.2
                                        # unless the patch version has exceeded 10 million.
                                   '>=',
                                   '==',  # Could miss hard negative. Wild cards not processed.
                                   '===',
                                   '~=',  # Could miss hard negative.  
                                   } and _version_tuple_from_str(version_identifier) >= min_python_version:
            return True

        # Misses an exhaustive list of version exclusions of earlier versions with '!='


        return False

    projects = collections.defaultdict(dict)

    # print('Processing projects: ', end='')

    for project_name in project_names:

        project_name = project_name.rstrip()

        # print(f'{project_name}, ', end='', flush=True)
        response = requests.get(f'https://www.wheelodex.org/json/projects/{project_name}/data')

        response.raise_for_status()

        meta_data = response.json()['data']['dist_info']['metadata']

        clauses = list(_python_version_clauses(meta_data))

        if any(excludes_unsupported_versions(comparison_operator, version_identifier)
               for comparison_operator, version_identifier in clauses):
            continue

        classifiers = list(_python_version_classifiers(meta_data))

        classifiers_older_than_min_supported = [
            classifier
            for classifier in classifiers
            if _version_tuple_from_str(classifier) < min_python_version
        ]

        if classifiers and classifiers_older_than_min_supported:
            continue


        # Don't str.casefold email addresses.  
        # If someone specified a ß and not an 'ss', preserve their choice.
        #
        # Use logical "or" instead of a default in .get, e.g. .get(key, '') 
        # as it is possible that meta_data['author_email'] is None.
        author = (meta_data.get('author_email') or '').lower()
        maintainer = (meta_data.get('maintainer_email') or '').lower()

        if author or maintainer:
            project_data = dict(
                meta_data = meta_data,
                clauses = clauses,
                classifiers = classifiers,
                classifiers_older_than_min_supported = classifiers_older_than_min_supported,
                )

        if author:
            projects[author][project_name] = project_data
        if maintainer:
            projects[maintainer][project_name] = project_data


    return projects
