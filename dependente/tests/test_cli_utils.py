"""
Test utility functions from cli.py
"""
import os
import shutil

import pytest

from ..cli import get_sources_and_config_files


class TestGetSourcesAndConfigFiles:
    """
    Test if get_sources_and_config_files() work as expected when only setup.cfg
    """

    @pytest.mark.parametrize(
        "sources",
        (
            ["install"],
            ["extras"],
            ["build"],
        ),
    )
    def test_files_missing(self, sources, tmp_path):
        """
        Test if error is raised when no configuration files are found in cwd
        """
        # Cd to tmp_path
        os.chdir(tmp_path)
        # Check if error is raised
        msg = "Missing 'pyproject.toml' and 'setup.cfg' files."
        with pytest.raises(FileNotFoundError, match=msg):
            get_sources_and_config_files(sources)

    @pytest.mark.parametrize(
        "sources",
        (
            ["install"],
            ["extras"],
            ["install", "extras"],
        ),
    )
    def test_setup_cfg(self, sources, setup_cfg, tmp_path):
        """
        Test when only setup.cfg exists
        """
        # Copy sample file to tmp_path and cd to tmp_path
        shutil.copy(src=setup_cfg, dst=tmp_path / "setup.cfg")
        os.chdir(tmp_path)
        # Check results with expected outcome
        result = get_sources_and_config_files(sources)
        expected = {"setup.cfg": sources}
        assert result == expected

    @pytest.mark.parametrize(
        "sources",
        (
            ["build"],
            ["install", "build"],
            ["extras", "build"],
            ["install", "build", "extras"],
        ),
    )
    def test_setup_with_build(self, sources, setup_cfg, tmp_path):
        """
        Test if error is raised when only setup.cfg exists and "build" is in
        sources.
        """
        # Copy sample file to tmp_path and cd to tmp_path
        shutil.copy(src=setup_cfg, dst=tmp_path / "setup.cfg")
        os.chdir(tmp_path)
        # Test if error is raised
        msg = "Missing 'pyproject.toml' file while asking for 'build' sources."
        with pytest.raises(FileNotFoundError, match=msg):
            get_sources_and_config_files(sources)

    @pytest.mark.parametrize(
        "sources",
        (
            ["build"],
            ["install"],
            ["extras"],
            ["install", "extras"],
            ["build", "install"],
            ["build", "extras"],
            ["build", "install", "extras"],
        ),
    )
    def test_pyproject_toml(self, sources, pyproject_toml, tmp_path):
        """
        Test when only pyproject.toml exists
        """
        # Copy sample file to tmp_path and cd to tmp_path
        shutil.copy(src=pyproject_toml, dst=tmp_path / "pyproject.toml")
        os.chdir(tmp_path)
        # Check results with expected outcome
        result = get_sources_and_config_files(sources)
        expected = {"pyproject.toml": sources}
        assert result == expected

    @pytest.mark.parametrize(
        "sources",
        (
            ["install"],
            ["extras"],
            ["install", "extras"],
        ),
    )
    def test_setup_cfg_and_pyproject_toml_no_build(
        self, sources, setup_cfg, pyproject_toml, tmp_path
    ):
        """
        Test when setup.cfg and pyproject.toml exist and build is not in
        sources.
        """
        # Copy sample files to tmp_path and cd to tmp_path
        shutil.copy(src=setup_cfg, dst=tmp_path / "setup.cfg")
        shutil.copy(src=pyproject_toml, dst=tmp_path / "pyproject.toml")
        os.chdir(tmp_path)
        # Check results with expected outcome
        result = get_sources_and_config_files(sources)
        expected = {"setup.cfg": sources}
        assert result == expected

    @pytest.mark.parametrize(
        "sources",
        (
            ["build"],
            ["build", "install"],
            ["build", "extras"],
            ["build", "install", "extras"],
        ),
    )
    def test_setup_cfg_and_pyproject_toml(
        self, sources, setup_cfg, pyproject_toml, tmp_path
    ):
        """
        Test when setup.cfg and pyproject.toml exist with build in sources
        """
        # Copy sample files to tmp_path and cd to tmp_path
        shutil.copy(src=setup_cfg, dst=tmp_path / "setup.cfg")
        shutil.copy(src=pyproject_toml, dst=tmp_path / "pyproject.toml")
        os.chdir(tmp_path)
        # Check results with expected outcome
        result = get_sources_and_config_files(sources)
        expected = {"pyproject.toml": ["build"]}
        if sources != ["build"]:
            expected["setup.cfg"] = [s for s in sources if s != "build"]
        assert result == expected
