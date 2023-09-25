# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Defines the command line interface.

Uses click to define a CLI around the ``main`` function.
"""
import sys
import traceback
from pathlib import Path

import click

from .converters import pin_to_oldest
from .parsers import (
    get_parser,
    validate_sources,
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

    * pyproject.toml (build-system > requires, project > dependencies and
        project.optional-dependencies)

    * setup.cfg (install_requires and options.extras_require)

    """
    reporter = Reporter(verbose)
    sources = source.split(",")
    validate_sources(sources)
    config_files = find_configuration_files(sources)
    # Parse dependencies
    dependencies = []
    for config_file, sources in config_files.items():
        reporter.echo(f"Parsing {config_file}")
        parser = get_parser(config_file)
        dependencies_found = parser.parse_requirements(sources)
        reporter.echo(f"  - {count(dependencies_found)} dependencies found")
        dependencies.extend(dependencies_found)
    # Pin to oldest versions
    if oldest:
        reporter.echo("Pinning dependencies to their oldest versions")
        dependencies = pin_to_oldest(dependencies)
    # Print gathered dependencies to stdout
    reporter.echo(
        f"Printing {count(dependencies)} dependencies to standard output",
    )
    for line in dependencies:
        click.echo(line)


def find_configuration_files(sources):
    """
    Find configuration files in current directory

    Return a dictionary with the names of configuration files that are present
    in the current directory as keys. The values will be the list of sources
    ("build", "install", "extras") that should be parsed from each of them.

    If only ``pyproject.toml`` is present, all sources will be parsed from it.
    If ``setup.cfg`` and ``pyproject.toml`` are present, then only the "build"
    dependencies will be parsed from ``pyproject.toml``, while "install" and
    "extras" will be obtained from ``setup.cfg``.

    Parameters
    ----------
    sources : list
        List of required sources. Must be a subset of {"build", "install",
        "extras"}.

    Returns
    -------
    dict

    Raises
    ------
    FileNotFoundError
        If ``setup.cfg`` and ``pyproject.toml`` are
        missing, or if only ``setup.cfg`` is present.
    """
    setup_cfg, pyproject_toml = Path("setup.cfg"), Path("pyproject.toml")
    if setup_cfg.is_file() and pyproject_toml.is_file():
        config_files = {
            "setup.cfg": [s for s in sources if s != "build"],
            "pyproject.toml": ["build"] if "build" in sources else [],
        }
    elif not setup_cfg.is_file() and pyproject_toml.is_file():
        config_files = {"pyproject.toml": sources}
    elif setup_cfg.is_file() and not pyproject_toml.is_file():
        raise FileNotFoundError("Missing 'pyproject.toml' file.")
    else:
        raise FileNotFoundError("Missing 'pyproject.toml' and 'setup.cfg' files.")
    return config_files


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
