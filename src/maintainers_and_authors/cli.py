import sys

from .api import email_addresses
from .core import _version_tuple_from_str

def main(args=sys.argv[1:]) -> int:

    min_python_version = _version_tuple_from_str(args[0]) if args else (float('inf'),)

    for email in email_addresses(sys.stdin, min_python_version):
        print(email)

    return 0