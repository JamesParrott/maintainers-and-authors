import sys

from . import api

def main(args=sys.argv[1:]) -> int:

    min_python_version = api.version_tuple_from_str(args[0]) if args else (float('inf'),)

    for email in api.email_addresses(sys.stdin, min_python_version):
        print(email)

    return 0