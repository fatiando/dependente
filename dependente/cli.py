# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Defines the command line interface.

Uses click to define a CLI around the ``main`` function.
"""
import sys

import click
import rich.console

from .converters import pin_to_oldest
from .parsers import (
    parse_requirements,
    parse_sources,
    read_pyproject_toml,
    read_setup_cfg,
)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--source",
    "-s",
    default="install",
    show_default=True,
    help="Which sources of dependency information to extract. "
    "Can be any combination of 'install,extras,build'.",
)
@click.option(
    "--oldest",
    "-o",
    default=False,
    show_default=True,
    is_flag=True,
    help="If enabled, will pin dependencies to the oldest accepted version.",
)
@click.option(
    "--verbose/--quiet",
    "-v/-q",
    default=True,
    show_default=True,
    help="Print information during execution / Don't print",
)
@click.version_option()
def main(source, oldest, verbose):
    """
    Dependente: Extract Python package dependencies from configuration files.

    Reads from the configuration files in the current directory and outputs to
    stdout a list of dependencies into a format accepted by pip.

    Supported formats:

    * pyproject.toml (only build-system > requires)

    * setup.cfg (install_requires and options.extras_require)

    """
    reporter = Reporter(verbose, style="bold blue", style_error="bold red")
    readers = {"setup.cfg": read_setup_cfg, "pyproject.toml": read_pyproject_toml}
    reporter.echo(f":rocket: Extracting dependencies: {source}")
    try:
        sources = parse_sources(source)
        dependencies = []
        for config_file in sources:
            if not sources[config_file]:
                continue
            reporter.echo(f":mag_right: Parsing {config_file}")
            config = readers[config_file]()
            dependencies_found = parse_requirements(config, sources[config_file])
            reporter.echo(f"   - {count(dependencies_found)} dependencies found")
            dependencies.extend(dependencies_found)
        if oldest:
            reporter.echo(
                ":mantelpiece_clock:  Pinning dependencies to their oldest versions"
            )
            dependencies = pin_to_oldest(dependencies)
        reporter.echo(
            f":printer:  Printing {count(dependencies)} dependencies to the "
            "standard output stream",
        )
        for line in dependencies:
            click.echo(line)
        reporter.echo(":partying_face: [bold green]Done![/] :partying_face:")
        sys.exit(0)
    except Exception:
        reporter.console.print_exception()
        reporter.error(
            "\n:fire::fire::fire: Error encountered while processing. "
            "See the message and traceback above. :fire::fire::fire:"
        )
        sys.exit(1)


def count(dependencies):
    """
    Count the number of dependencies in a list.
    Ignores any comments (entries starting with #).
    """
    return len([i for i in dependencies if not i.strip().startswith("#")])


class Reporter:
    """
    Small wrapper around :class:`rich.console.Console` to control verbosity.

    Use *echo* to print according to verbosity settings and *error* to always
    print regardless of settings.
    """

    def __init__(self, verbose, style, style_error):
        self.verbose = verbose
        self.style = style
        self.style_error = style_error
        self.console = rich.console.Console(stderr=True, highlight=False)

    def _print(self, message, style, **kwargs):
        """
        Print the message with the given style using rich.
        """
        arguments = {"style": style}
        arguments.update(kwargs)
        self.console.print(message, **arguments)

    def echo(self, message, **kwargs):
        """
        Print the message if verbosity is enabled.
        """
        if self.verbose:
            self._print(message, style=self.style, **kwargs)

    def error(self, message, **kwargs):
        """
        Print the message regardless of verbosity settings.
        """
        self._print(message, style=self.style_error, **kwargs)
