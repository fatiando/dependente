# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Test the functions that extract content from configuration files.
"""
from pathlib import Path

import pytest

from ..parsers import parse_sources


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
