# Copyright (c) 2021 Leonardo Uieda.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT
"""
Test functions for converting/transforming dependencies.
"""
import pytest

from ..converters import pin_to_oldest


@pytest.mark.parametrize(
    "requirements,expected",
    [
        (["bla>=12"], ["bla==12"]),
        (["bla<12"], ["bla<12"]),
        (["bla>=11,<12"], ["bla==11"]),
        (["# meh", "bla>=11,<12", "# foo"], ["# meh", "bla==11", "# foo"]),
    ],
    ids=["lower", "upper", "both", "comment"],
)
def test_pin_to_oldest(requirements, expected):
    "Check that pinning works"
    assert expected == pin_to_oldest(requirements)
