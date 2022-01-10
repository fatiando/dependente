# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Defines the command line interface.

Uses click to define a CLI around the ``main`` function.
"""
import sys
import traceback

import click

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
    Dependente: Inspect Python package dependencies

    Reads from the configuration files in the current directory and outputs to
    stdout a list of dependencies into a format accepted by pip.

    Supported formats:

    * pyproject.toml (only build-system > requires)

    * setup.cfg (install_requires and options.extras_require)

    """
    reporter = Reporter(verbose)
    readers = {"setup.cfg": read_setup_cfg, "pyproject.toml": read_pyproject_toml}
    reporter.echo(f"Extracting dependencies: {source}")
    try:
        sources = parse_sources(source)
        dependencies = []
        for config_file in sources:
            if not sources[config_file]:
                continue
            reporter.echo(f"Parsing {config_file}")
            config = readers[config_file]()
            dependencies_found = parse_requirements(config, sources[config_file])
            reporter.echo(f"  - {count(dependencies_found)} dependencies found")
            dependencies.extend(dependencies_found)
        if oldest:
            reporter.echo("Pinning dependencies to their oldest versions")
            dependencies = pin_to_oldest(dependencies)
        reporter.echo(
            f"Printing {count(dependencies)} dependencies to standard output",
        )
        for line in dependencies:
            click.echo(line)
        reporter.echo("Done!")
    except Exception:
        reporter.error("\nError encountered while processing:\n")
        reporter.error(traceback.format_exc())
        reporter.error("Oh no! Something went wrong. See the messages above.")
        sys.exit(1)


def count(dependencies):
    """
    Count the number of dependencies in a list.
    Ignores any comments (entries starting with #).
    """
    return len([i for i in dependencies if not i.strip().startswith("#")])


class Reporter:
    """
    Small wrapper around click.echo to control verbosity.

    Use *echo* to print according to verbosity settings and *error* to always
    print regardless of settings.
    """

    def __init__(self, verbose):
        self.verbose = verbose

    def echo(self, message):
        """
        Print the message if verbosity is enabled.
        """
        if self.verbose:
            click.echo(message, err=True)

    def error(self, message):
        """
        Print the message regardless of verbosity settings.
        """
        click.echo(message, err=True)
