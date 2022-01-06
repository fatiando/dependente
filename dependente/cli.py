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
    "--verbose/--quiet",
    "-v/-q",
    default=True,
    show_default=True,
    help="Print information during execution / Don't print",
)
@click.version_option()
def main(source, verbose):
    """
    Dependente: Extract Python package dependencies from configuration files.

    Reads from the configuration files in the current directory and outputs to
    stdout a list of dependencies into a format accepted by pip.

    Supported formats:

    * pyproject.toml (only build-system > requires)

    * setup.cfg (install_requires and options.extras_require)

    """
    console = make_console(verbose)
    console_error = make_console(verbose=True)
    style = "bold blue"
    console.print(
        f":rocket: Extracting dependencies: {source}",
        style=style,
    )
    sources = parse_sources(source)
    readers = {"setup.cfg": read_setup_cfg, "pyproject.toml": read_pyproject_toml}
    dependencies = []
    for config_file in sources:
        if not sources[config_file]:
            continue
        try:
            console.print(f":mag_right: Parsing {config_file}: ", end="", style=style)
            config = readers[config_file]()
            dependencies_found = parse_requirements(config, sources[config_file])
            console.print(
                f"{count(dependencies_found)} dependencies found", style=style
            )
            dependencies.extend(dependencies_found)
        except Exception:
            style = "bold red"
            console_error.rule(
                ":fire: The following errors were encountered: :fire:", style=style
            )
            console_error.print_exception(suppress=[click, rich])
            console_error.rule(":fire: End of error messages :fire:", style=style)
            console_error.print()
            console_error.print(
                f":pensive: Sorry! Could not extract dependencies from '{config_file}'",
                style=style,
            )
            sys.exit(1)
    console.print(
        f":printer:  Printing {count(dependencies)} dependencies to the "
        "standard output stream",
        style=style,
    )
    for line in dependencies:
        click.echo(line)
    console.print(":partying_face: [bold green]Done![/] :partying_face:", style=style)
    sys.exit(0)


def count(dependencies):
    """
    Count the number of dependencies in a list.

    Ignores any comments (entries starting with #).
    """
    return len([i for i in dependencies if not i.strip().startswith("#")])


def make_console(verbose):
    """
    Start up the :class:`rich.console.Console` instance we'll use.

    Parameters
    ----------
    verbose : bool
        Whether or not to print status messages to stderr.

    Returns
    -------
    console
        A Console instance.
    """
    return rich.console.Console(stderr=True, quiet=not verbose, highlight=False)
