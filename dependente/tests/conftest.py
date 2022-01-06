# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Fixtures for pytest
"""
from pathlib import Path

import pytest


@pytest.fixture()
def setup_cfg():
    "The text contents of the test file."
    return str(Path(__file__).parent / "data" / "sample_setup.cfg")


@pytest.fixture()
def setup_cfg_config():
    "The parsed contents of the file."
    contents = {
        "options": {
            "python_requires": ">=3.6",
            "install_requires": "click>=8.0.0,<9.0.0\nrich>=9.6.0,<11.0.0\ntomli>=1.0.0,<3.0.0",
        },
        "options.extras_require": {
            "jupyter": "nbformat>=5.1",
        },
    }
    return contents


@pytest.fixture()
def setup_cfg_install():
    "The install requirements"
    contents = [
        "click>=8.0.0,<9.0.0",
        "rich>=9.6.0,<11.0.0",
        "tomli>=1.0.0,<3.0.0",
    ]
    return contents


@pytest.fixture()
def setup_cfg_extras():
    "The extra requirements"
    contents = [
        "nbformat>=5.1",
    ]
    return contents


@pytest.fixture()
def pyproject_toml():
    "The text contents of the test file."
    return str(Path(__file__).parent / "data" / "sample_pyproject.toml")


@pytest.fixture()
def pyproject_toml_config():
    "The parsed contents of the file."
    contents = {
        "build-system": {
            "requires": [
                "setuptools>=45",
                "setuptools_scm>=6.2",
                "wheel",
            ]
        },
    }
    return contents


@pytest.fixture()
def pyproject_toml_build():
    "The build requirements"
    contents = [
        "setuptools>=45",
        "setuptools_scm>=6.2",
        "wheel",
    ]
    return contents
