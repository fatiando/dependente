# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Test the functions that extract content from configuration files.

The fixtures (arguments to the test functions) are defined in conftest.py
"""
import pytest

from ..parsers import (
    get_pyproject_toml_build,
    get_setup_cfg_extras,
    get_setup_cfg_install,
    parse_requirements,
    parse_sources,
    read_pyproject_toml,
    read_setup_cfg,
)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("install", {"setup.cfg": ["install_requires"], "pyproject.toml": []}),
        ("build", {"setup.cfg": [], "pyproject.toml": ["build-system"]}),
        ("extras", {"setup.cfg": ["options.extras_require"], "pyproject.toml": []}),
        (
            "install,extras",
            {
                "setup.cfg": ["options.extras_require", "install_requires"],
                "pyproject.toml": [],
            },
        ),
        (
            "extras,build",
            {
                "setup.cfg": ["options.extras_require"],
                "pyproject.toml": ["build-system"],
            },
        ),
        (
            "build,extras,install",
            {
                "setup.cfg": ["options.extras_require", "install_requires"],
                "pyproject.toml": ["build-system"],
            },
        ),
    ],
    ids=["install", "build", "extras", "install,extras", "extras,build", "all"],
)
def test_parse_sources(source, expected):
    "Check the parsing of input data sources"
    assert expected == parse_sources(source)


def test_parse_sources_invalid():
    "Should raise an exception on invalid input"
    with pytest.raises(ValueError) as error:
        parse_sources("something")
    assert "'something'" in str(error)


def test_read_setup_cfg(setup_cfg, setup_cfg_config):
    "Check that setup.cfg is read properly"
    assert setup_cfg_config == read_setup_cfg(setup_cfg)


def test_read_pyproject_toml(pyproject_toml, pyproject_toml_config):
    "Check that pyproject.toml is read properly"
    assert pyproject_toml_config == read_pyproject_toml(pyproject_toml)


def test_parse_requirements_install(setup_cfg_config, setup_cfg_install):
    "Check that setup.cfg parses install requirements properly"
    parsed = [
        line
        for line in parse_requirements(setup_cfg_config, ["install_requires"])
        if not line.startswith("#")
    ]
    assert setup_cfg_install == parsed


def test_parse_requirements_extras(setup_cfg_config, setup_cfg_extras):
    "Check that setup.cfg parses extra requirements properly"
    parsed = [
        line
        for line in parse_requirements(setup_cfg_config, ["options.extras_require"])
        if not line.startswith("#")
    ]
    assert setup_cfg_extras == parsed


def test_parse_requirements_build(pyproject_toml_config, pyproject_toml_build):
    "Check that pyproject.toml parses all requirements properly"
    parsed = [
        line
        for line in parse_requirements(pyproject_toml_config, ["build-system"])
        if not line.startswith("#")
    ]
    assert pyproject_toml_build == parsed


def test_parse_requirements_multiple(
    setup_cfg_config, setup_cfg_extras, setup_cfg_install
):
    "Check that setup.cfg parses all requirements properly"
    parsed = [
        line
        for line in parse_requirements(
            setup_cfg_config, ["options.extras_require", "install_requires"]
        )
        if not line.startswith("#")
    ]
    expected = setup_cfg_extras + setup_cfg_install
    assert expected == parsed


def test_parse_requirements_install_fail():
    "Check that parsing fails with an exception"
    with pytest.raises(ValueError) as error:
        get_setup_cfg_install({"options": {"something": []}})
    assert "Missing 'install_requires'" in str(error)


def test_parse_requirements_extras_fail():
    "Check that parsing fails with an exception"
    with pytest.raises(ValueError) as error:
        get_setup_cfg_extras({"options": {"something": []}})
    assert "Missing 'options.extras_require'" in str(error)


def test_parse_requirements_build_fail():
    "Check that parsing fails with an exception"
    with pytest.raises(ValueError) as error:
        get_pyproject_toml_build({"meh": ["something"]})
    assert "Missing 'build-system'" in str(error)
    with pytest.raises(ValueError) as error:
        get_pyproject_toml_build({"build-system": {"something": []}})
    assert "Missing 'requires'" in str(error)
