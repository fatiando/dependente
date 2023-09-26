# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Test the functions that extract content from configuration files.

The fixtures (arguments to the test functions) are defined in conftest.py
"""
import pytest

from ..parsers import ParserPyprojectToml, ParserSetupCfg, get_parser, validate_sources


@pytest.mark.parametrize(
    "fname, expected_class",
    [
        ("setup.cfg", ParserSetupCfg),
        ("pyproject.toml", ParserPyprojectToml),
        ("invalid.file", None),
    ],
    ids=["setup.cfg", "pyproject.toml", "invalid.file"],
)
def test_get_parser(fname, expected_class):
    """
    Test get_parser function
    """
    if expected_class is not None:
        assert isinstance(get_parser(fname), expected_class)
    else:
        with pytest.raises(ValueError, match="Invalid configuration file"):
            get_parser(fname)


class TestValidateSources:
    """
    Test validate_sources function
    """

    @pytest.mark.parametrize(
        "sources",
        (
            ["build"],
            ["install"],
            ["extras"],
            ["build", "install", "extras"],
            ["extras", "build", "install"],
        ),
    )
    def test_valid_sources(self, sources):
        """
        Test if the function don't raises errors after valid sources
        """
        validate_sources(sources)

    @pytest.mark.parametrize("sources", (["invalid"], ["build", "extras", "invalid"]))
    def test_invalid_sources(self, sources):
        """
        Test if the function raises errors after invalid sources
        """
        with pytest.raises(ValueError, match="Invalid sources"):
            validate_sources(sources)

    def test_repeated_sources(self):
        """
        Test if the function raises errors after repeated sources
        """
        sources = ["build", "extras", "build"]
        with pytest.raises(ValueError, match="Found repeated sources"):
            validate_sources(sources)


class TestSetupCfgParser:
    """
    Test parser class for setup.cfg files.
    """

    def test_config(self, setup_cfg, setup_cfg_config):
        """
        Test if config was correctly read from file
        """
        parser = ParserSetupCfg(setup_cfg)
        assert parser.config == setup_cfg_config

    @pytest.mark.parametrize(
        "sources",
        (
            ["build"],
            ["build", "install"],
            ["build", "install", "extras"],
            ["install", "extras", "build"],
        ),
    )
    def test_parse_build(self, setup_cfg, sources):
        """Test if error is raised when "build" requirements are passed."""
        parser = ParserSetupCfg(setup_cfg)
        msg = "Cannot parse 'build' sources from setup.cfg."
        with pytest.raises(ValueError, match=msg):
            parser.parse_requirements(sources)

    def test_parse_install(self, setup_cfg, install_dependencies):
        """Test if parsed install requirements are correct."""
        parser = ParserSetupCfg(setup_cfg)
        parsed = [
            line
            for line in parser.parse_requirements(["install"])
            if not line.startswith("#")
        ]
        assert install_dependencies == parsed

    def test_parse_extras(self, setup_cfg, extras_dependencies):
        """Test if parsed extras dependencies are correct."""
        parser = ParserSetupCfg(setup_cfg)
        parsed = [
            line
            for line in parser.parse_requirements(["extras"])
            if not line.startswith("#")
        ]
        assert extras_dependencies == parsed

    @pytest.mark.parametrize("sources", (["install", "extras"], ["extras", "install"]))
    def test_parse_multiple(
        self, sources, setup_cfg, install_dependencies, extras_dependencies
    ):
        """Test if parsing multiple sources works as expected."""
        parser = ParserSetupCfg(setup_cfg)
        parsed = [
            line
            for line in parser.parse_requirements(sources)
            if not line.startswith("#")
        ]
        assert install_dependencies + extras_dependencies == parsed


class TestPyprojectTomlParser:
    """
    Test parser class for pyproject.toml files.
    """

    def test_config(self, pyproject_toml, pyproject_toml_config):
        """
        Test if config was correctly read from file
        """
        parser = ParserPyprojectToml(pyproject_toml)
        assert parser.config == pyproject_toml_config

    def test_parse_build(self, pyproject_toml, build_dependencies):
        """Test if error is raised when "build" requirements are passed."""
        parser = ParserPyprojectToml(pyproject_toml)
        parsed = [
            line
            for line in parser.parse_requirements(["build"])
            if not line.startswith("#")
        ]
        assert build_dependencies == parsed

    def test_parse_install(self, pyproject_toml, install_dependencies):
        """Test if parsed install requirements are correct."""
        parser = ParserPyprojectToml(pyproject_toml)
        parsed = [
            line
            for line in parser.parse_requirements(["install"])
            if not line.startswith("#")
        ]
        assert install_dependencies == parsed

    def test_parse_extras(self, pyproject_toml, extras_dependencies):
        """Test if parsed extras dependencies are correct."""
        parser = ParserPyprojectToml(pyproject_toml)
        parsed = [
            line
            for line in parser.parse_requirements(["extras"])
            if not line.startswith("#")
        ]
        assert extras_dependencies == parsed

    @pytest.mark.parametrize(
        "sources",
        (
            ["build", "install"],
            ["build", "extras"],
            ["install", "extras"],
            ["extras", "install"],
            ["build", "install", "extras"],
            ["extras", "install", "build"],
        ),
    )
    def test_parse_multiple(
        self,
        sources,
        pyproject_toml,
        install_dependencies,
        extras_dependencies,
        build_dependencies,
    ):
        """Test if parsing multiple sources works as expected."""
        parser = ParserPyprojectToml(pyproject_toml)
        parsed = [
            line
            for line in parser.parse_requirements(sources)
            if not line.startswith("#")
        ]
        expected = []
        if "build" in sources:
            expected += build_dependencies
        if "install" in sources:
            expected += install_dependencies
        if "extras" in sources:
            expected += extras_dependencies
        assert expected == parsed
