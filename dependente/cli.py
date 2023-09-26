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
from .parsers import get_parser, validate_sources


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
    try:
        config_files = get_sources_and_config_files(sources)
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
        reporter.echo("Done!")
    except Exception:
        reporter.error("\nError encountered while processing:\n")
        reporter.error(traceback.format_exc())
        reporter.error("Oh no! Something went wrong. See the messages above.")
        sys.exit(1)


def get_sources_and_config_files(sources):
    """
    Get configuration files in working directory and corresponding sources

    Find configuration files in current directory and sort out which sources
    should be parsed from which config file.

    Parameters
    ----------
    sources : list of str
        List containing a subset of valid sources ("build", "install",
        "extras").

    Returns
    -------
    config_files : dict
        Dictionary with config files as keys. Their values are a list of
        sources that should be parsed from each one of them.

    Raises
    ------
    FileNotFoundError
        If both ``setup.cfg`` and ``pyproject.toml`` are missing in the current
        directory.
        If "build" is in ``sources``, but ``pyproject.toml`` is not present in
        the current directory.
    """
    # Get configuration files in working directory
    fnames = ("pyproject.toml", "setup.cfg")
    config_fnames = [fname for fname in fnames if Path(fname).is_file()]
    if not config_fnames:
        raise FileNotFoundError("Missing 'pyproject.toml' and 'setup.cfg' files.")
    # Sort out sources
    if "build" in sources and "pyproject.toml" not in config_fnames:
        raise FileNotFoundError(
            "Missing 'pyproject.toml' file while asking for 'build' sources. "
            "The 'build' sources can only be parsed from a 'pyproject.toml' file."
        )
    if "setup.cfg" in config_fnames:
        config_files = {
            "pyproject.toml": ["build"] if "build" in sources else [],
            "setup.cfg": [s for s in sources if s != "build"],
        }
    else:
        config_files = {"pyproject.toml": sources}
    config_files = {key: value for key, value in config_files.items() if value}
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
