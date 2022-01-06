# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Functions for manipulating/converting dependency lists.
"""


def pin_to_oldest(requirements):
    """
    Convert the list of requirements to pin the oldest supported version.

    Parameters
    ----------
    requirements : list
        List of requirements (strings). May contain comments (starting with #)
        that are copied verbatim to the output.

    Returns
    -------
    oldest : list
        List of requirements pinned to the oldest supported version.
    """
    oldest = [
        package.split(",")[0].replace(">=", "==").strip() for package in requirements
    ]
    return oldest
