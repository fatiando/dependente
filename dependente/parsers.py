# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Functions for extracting the dependency information from files.
"""
import configparser

import tomli


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
    valid_sources = {
        "install": {"file": "setup.cfg", "option": "install_requires"},
        "extras": {"file": "setup.cfg", "option": "options.extras_require"},
        "build": {"file": "pyproject.toml", "option": "build-system"},
    }
    for entry in sorted(source.strip().split(",")):
        if entry not in valid_sources:
            raise ValueError(
                f"Invalid source '{entry}'. Must be one of {valid_sources}."
            )
        sources[valid_sources[entry]["file"]].append(valid_sources[entry]["option"])
    return sources


def read_setup_cfg(fname="setup.cfg"):
    """
    Read the setup.cfg file into a dictionary.
    """
    config = configparser.ConfigParser()
    config.read(fname)
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


def read_pyproject_toml(fname="pyproject.toml"):
    """
    Read the pyproject.toml file into a dictionary.
    """
    with open(fname, "rb") as config_source:
        config = tomli.load(config_source)
    return config


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
