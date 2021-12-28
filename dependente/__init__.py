# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Dependente: Extract Python package dependencies from configuration files.

The _version module is generated automatically by setuptools_scm at build time.
"""
from . import _version

__version__ = f"v{_version.version}"
