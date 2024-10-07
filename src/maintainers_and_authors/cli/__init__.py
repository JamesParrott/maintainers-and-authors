# SPDX-FileCopyrightText: 2024-present JamesParrott <80779630+JamesParrott@users.noreply.github.com>
#
# SPDX-License-Identifier: MIT
import click

from maintainers_and_authors.__about__ import __version__


@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="Maintainers and Authors")
def maintainers_and_authors():
    click.echo("Hello world!")
