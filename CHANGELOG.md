# Changelog

## Version 0.1.0

*Release date*: 2022/01/06

**First release of *Dependente*, a tool for inspecting Python package
dependencies**

This is a small command-line program for extracting dependencies from Python
project files (`pyproject.toml` and `setup.cfg`) and converting them into
`requirements.txt`-type files for use with `pip` and `conda`.
The main reason to do so is to control and customize the testing environment on
continuous integration (CI) while avoiding repeating the list of dependencies
in multiple places. That's what we use it for.
