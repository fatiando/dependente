# Copyright (c) 2021 The Dependente Developers.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
# This code is part of the Fatiando a Terra project (https://www.fatiando.org).
"""
Functions for extracting the dependency information from files.
"""

import configparser
from pathlib import Path

import tomli


def get_parser(fname):
    """
    Return instance of a Parser class based on the type of config file.
    """
    fname = Path(fname)
    if fname.suffix == ".cfg":
        parser = ParserSetupCfg(fname)
    elif fname.suffix == ".toml":
        parser = ParserPyprojectToml(fname)
    else:
        raise ValueError(
            f"Invalid configuration file '{fname}' with suffix '{fname.suffix}'. "
            "Only '.cfg' and '.toml' are supported."
        )
    return parser


def validate_sources(sources):
    """
    Validate sources

    Check if sources is form by a subset of "build", "install" and "extras".

    Parameters
    ----------
    sources : list
        List of sources. Valid sources are "build", "install" and "extras".
    """
    if not sources:
        raise ValueError(
            "No sources were provided. "
            "Please choose a subset of 'build', 'install' and 'extras'."
        )
    valid_sources = set(["build", "install", "extras"])
    if not set(sources).issubset(valid_sources):
        invalid = valid_sources - set(sources)
        raise ValueError(
            f"Invalid sources '{invalid}'. " f"Choose a subset of '{valid_sources}'."
        )
    repeated_sources = [s for s in sources if sources.count(s) > 1]
    if repeated_sources:
        raise ValueError(f"Found repeated sources: '{repeated_sources}'.")


class ParserSetupCfg:
    """
    Parser for setup.cfg files
    """

    def __init__(self, fname):
        fname = Path(fname)
        self.fname = fname

    @property
    def config(self):
        """
        Return content of the setup.cfg file into a dictionary
        """
        if not hasattr(self, "_config"):
            config = configparser.ConfigParser()
            # Use read_file to get a FileNotFoundError if setup.cfg is missing.
            # Using read returns an empty config instead of raising an
            # exception.
            with open(self.fname, "rt") as config_source:
                config.read_file(config_source)
            self._config = {
                section: dict(
                    (key, value.strip()) for key, value in config.items(section)
                )
                for section in config.sections()
            }
        return self._config

    def parse_requirements(self, sources):
        """
        Parse requirements from setup.cfg config file
        """
        validate_sources(sources)
        dependencies = []
        if "build" in sources:
            raise ValueError("Cannot parse 'build' sources from setup.cfg.")
        if "install" in sources:
            dependencies += self.parse_install_dependencies()
        if "extras" in sources:
            dependencies += self.parse_extra_dependencies()
        return dependencies

    def parse_install_dependencies(self):
        """
        Parse install requirements from setup.cfg config file
        """
        source = "install_requires"
        if source not in self.config["options"]:
            raise ValueError(f"Missing '{source}' field in setup.cfg.")
        packages = [
            package.strip()
            for package in self.config["options"][source].strip().split("\n")
        ]
        requirements = ["# Install (run-time) dependencies from setup.cfg"] + packages
        return requirements

    def parse_extra_dependencies(self):
        """
        Parse extra requirements from setup.cfg config file
        """
        source = "options.extras_require"
        if source not in self.config:
            raise ValueError(f"Missing '{source}' section in setup.cfg.")
        requirements = ["# Extra (optional) dependencies from setup.cfg"]
        for section in self.config[source]:
            requirements.append(f"#   extra: {section}")
            for package in self.config[source][section].strip().split("\n"):
                requirements.append(package.strip())
        return requirements


class ParserPyprojectToml:
    """
    Parser for pyproject.toml files
    """

    def __init__(self, fname):
        fname = Path(fname)
        self.fname = fname

    @property
    def config(self):
        """
        Return content of the pyproject.toml file into a dictionary
        """
        if not hasattr(self, "_config"):
            with open(self.fname, "rb") as config_source:
                self._config = tomli.load(config_source)
        return self._config

    def parse_requirements(self, sources):
        """
        Parse requirements from setup.cfg config file
        """
        validate_sources(sources)
        dependencies = []
        if "build" in sources:
            dependencies += self.parse_build_dependencies()
        if "install" in sources:
            dependencies += self.parse_install_dependencies()
        if "extras" in sources:
            dependencies += self.parse_extra_dependencies()
        return dependencies

    def parse_build_dependencies(self):
        """
        Parse build requirements from setup.cfg config file
        """
        source = "build-system"
        if source not in self.config:
            raise ValueError(f"Missing '{source}' section in pyproject.toml.")
        if "requires" not in self.config[source]:
            raise ValueError(
                f"Missing 'requires' entry from the '{source}' section in "
                "pyproject.toml."
            )
        requirements = ["# Build dependencies from pyproject.toml"]
        for package in self.config[source]["requires"]:
            requirements.append(package.strip())
        return requirements

    def parse_install_dependencies(self):
        """
        Parse install requirements from setup.cfg config file
        """
        source = "project"
        if source not in self.config:
            raise ValueError(f"Missing '{source}' section in pyproject.toml.")
        if "dependencies" not in self.config[source]:
            raise ValueError(
                f"Missing 'dependencies' entry from the '{source}' section in "
                "pyproject.toml."
            )
        requirements = ["# Install dependencies from pyproject.toml"]
        for package in self.config[source]["dependencies"]:
            requirements.append(package.strip().replace(" ", ""))
        return requirements

    def parse_extra_dependencies(self):
        """
        Parse extra requirements from setup.cfg config file
        """
        source = "project"
        subsource = "optional-dependencies"
        if source not in self.config:
            raise ValueError(f"Missing '{source}' section in pyproject.toml.")
        if subsource not in self.config[source]:
            raise ValueError(
                f"Missing '{source}.{subsource}' section in pyproject.toml."
            )
        requirements = ["# Extra (optional) dependencies from pyproject.toml"]
        for section, packages in self.config[source][subsource].items():
            requirements.append(f"#   extra: {section}")
            for package in packages:
                requirements.append(package.strip().replace(" ", ""))
        return requirements
