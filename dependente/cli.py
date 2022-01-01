# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Defines the command line interface.

Uses click to define a CLI around the ``main`` function.
"""
import configparser
import sys

import click
import rich.console
import tomli


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
    parsers = {"setup.cfg": parse_setup_cfg, "pyproject.toml": parse_pyproject_toml}
    readers = {"setup.cfg": read_setup_cfg, "pyproject.toml": read_pyproject_toml}
    dependencies = []
    for config_file in sources:
        if not sources[config_file]:
            continue
        try:
            console.print(f":mag_right: Parsing {config_file}: ", end="", style=style)
            config = readers[config_file]()
            dependencies_found = parsers[config_file](config, sources[config_file])
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


def parse_sources(source):
    """
    Parse the input string for sources and separate based on config file type.

    Parameters
    ----------
    source : str
        Input source specification.

    Returns
    -------
    sources : dict
        Dictionary of parse sources. Keys are config file names.
    """
    sources = {"setup.cfg": [], "pyproject.toml": []}
    valid_sources = {"install", "extras", "build"}
    for entry in source.strip().split(","):
        if entry not in valid_sources:
            raise ValueError(
                f"Invalid source '{entry}'. Must be one of {valid_sources}."
            )
        elif entry == "install":
            sources["setup.cfg"].append("install_requires")
        elif entry == "extras":
            sources["setup.cfg"].append("options.extras_require")
        elif entry == "build":
            sources["pyproject.toml"].append("build-system")
    return sources


def read_setup_cfg():
    """
    Read the setup.cfg file into a dictionary.
    """
    config = configparser.ConfigParser()
    config.read("setup.cfg")
    return config


def read_pyproject_toml():
    """
    Read the pyproject.toml file into a dictionary.
    """
    with open("pyproject.toml", "rb") as config_source:
        config = tomli.load(config_source)
    return config


def parse_setup_cfg(config, sources):
    """
    Parse the sources from setup.cfg.

    Parameters
    ----------
    config : dict
        The configuration file read using configparser.
    sources : list
        List of section names from the config file.

    Returns
    -------
    dependencies : list
        List of dependencies read from the config file. Includes some comments.

    """
    requirements = []
    for source in sources:
        if source == "install_requires":
            if source not in config["options"]:
                raise ValueError(f"Missing '{source}' field in setup.cfg.")
            requirements.append("# Install (run-time) dependencies from setup.cfg")
            for package in config["options"][source].strip().split("\n"):
                requirements.append(package.strip())
        elif source == "options.extras_require":
            if source not in config:
                raise ValueError(f"Missing '{source}' section in setup.cfg.")
            requirements.append("# Extra (optional) dependencies from setup.cfg")
            for section in config[source]:
                requirements.append(f"#   extra: {section}")
                for package in config[source][section].strip().split("\n"):
                    requirements.append(package.strip())
    return requirements


def parse_pyproject_toml(config, sources):
    """
    Parse the sources from pyproject.toml.

    Parameters
    ----------
    config : dict
        The configuration file read using tomli.
    sources : list
        List of section names from the config file.

    Returns
    -------
    dependencies : list
        List of dependencies read from the config file. Includes some comments.

    """
    requirements = []
    for source in sources:
        if source == "build-system":
            if source not in config:
                raise ValueError(f"Missing '{source}' section in pyproject.toml.")
            requirements.append("# Build dependencies from pyproject.toml")
            if "requires" not in config[source]:
                raise ValueError(
                    f"Missing 'requires' entry from the '{source}' section in "
                    "pyproject.toml."
                )
            for package in config[source]["requires"]:
                requirements.append(package.strip())
    return requirements
