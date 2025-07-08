import sys

from . import api


def main(args=sys.argv[1:]) -> int:
    min_python_version = api.version_tuple_from_str(args[0]) if args else ()

    for emails in api.email_addresses(min_python_version):
        print(f"<{'>, <'.join(email for email in emails)}>")

    return 0
