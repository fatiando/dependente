# Dependente: Inspect Python package dependencies

Part of the [Fatiando a Terra][fatiando] project

[![Latest release on PyPI](https://img.shields.io/pypi/v/dependente.svg?style=flat-square)][pypi]
[![Latest release on conda-forge](https://img.shields.io/conda/vn/conda-forge/dependente.svg?style=flat-square)][conda-forge]
[![Test coverage report](https://img.shields.io/codecov/c/github/fatiando/dependente/main?style=flat-square)][coverage]
[![Compatible Python versions](https://img.shields.io/pypi/pyversions/dependente.svg?style=flat-square)][pypi]

## About

*Dependente* is a small command-line program for extracting
dependencies from Python project files (`pyproject.toml` and `setup.cfg`)
and converting them into `requirements.txt`-type files for use with
`pip` and `conda`.

The main reason to do so is to control and customize the testing
environment on continuous integration (CI) while avoiding repeating
the list of dependencies in multiple places.

> This project was inspired by some of the GitHub Actions configuration of the
> [MetPy](https://github.com/Unidata/MetPy) project.

## Installing

*Dependente* is available from PyPI:

```
python -m pip install dependente
```

and conda-forge:

```
conda install dependente -c conda-forge
```

## Using

> In these examples, we'll parse the dependencies from
> [Pooch](https://github.com/fatiando/pooch).

Parse the install (run-time) dependencies from `setup.cfg`:

```
$ dependente > requirements.txt
Extracting dependencies: install
Parsing setup.cfg
  - 3 dependencies found
Printing 3 dependencies to standard output
Done!

$ cat requirements.txt
# Install (run-time) dependencies from setup.cfg
appdirs>=1.3.0
packaging>=20.0
requests>=2.19.0
```

Also read the build dependencies from `pyproject.toml` and extra dependencies
from `setup.cfg`:

```
$ dependente --source install,build,extras > requirements-all.txt
Extracting dependencies: install,build,extras
Parsing setup.cfg
  - 6 dependencies found
Parsing pyproject.toml
  - 3 dependencies found
Printing 9 dependencies to standard output
Done!

$ cat requirements-all.txt
# Extra (optional) dependencies from setup.cfg
#   extra: progress
tqdm>=4.41.0,<5.0.0
#   extra: sftp
paramiko>=2.7.0
#   extra: xxhash
xxhash>=1.4.3
# Install (run-time) dependencies from setup.cfg
appdirs>=1.3.0
packaging>=20.0
requests>=2.19.0
# Build dependencies from pyproject.toml
setuptools>=45
wheel
setuptools_scm[toml]>=6.2
```

Pin the dependencies to their oldest supported version (useful for testing
in CI):

```
$ dependente --source install,extras --oldest > requirements-oldest.txt
Extracting dependencies: install,extras
Parsing setup.cfg
  - 6 dependencies found
Pinning dependencies to their oldest versions
Printing 6 dependencies to standard output
Done!

$ cat requirements-oldest.txt
# Extra (optional) dependencies from setup.cfg
#   extra: progress
tqdm==4.41.0
#   extra: sftp
paramiko==2.7.0
#   extra: xxhash
xxhash==1.4.3
# Install (run-time) dependencies from setup.cfg
appdirs==1.3.0
packaging==20.0
requests==2.19.0
```

See a full list of options:

```
$ dependente --help
Usage: dependente [OPTIONS]

  Dependente: Inspect Python package dependencies

  Reads from the configuration files in the current directory and outputs to
  stdout a list of dependencies into a format accepted by pip.

  Supported formats:

  * pyproject.toml (only build-system > requires)

  * setup.cfg (install_requires and options.extras_require)

Options:
  -s, --source TEXT            Which sources of dependency information to
                               extract. Can be any combination of
                               'install,extras,build'.  [default: install]
  -o, --oldest                 If enabled, will pin dependencies to the oldest
                               accepted version.  [default: False]
  -v, --verbose / -q, --quiet  Print information during execution / Don't
                               print  [default: verbose]
  --version                    Show the version and exit.
  -h, --help                   Show this message and exit.
```

### Limitations

The current implementation is a proof-of-concept and has some limitations:

* Input files must be in the current working directory.
* Reads all extra dependencies simultaneously (can't separate between different
  `option.extras_requires` fields).
* Only supports reading from `setup.cfg` and `pyproject.toml` (build
  dependencies only).

Of course, all of these could be addressed if there is enough interest.
Issues and PRs are welcome!

## Dependencies

We use the following dependencies (see `setup.cfg` for specific version
constraints):

* [click](https://click.palletsprojects.com) for building the command-line
  interface.
* [tomli](https://github.com/hukkin/tomli) to parse the TOML configuration
  files.

## Contacting Us

Find out more about how to reach us at
[fatiando.org/contact][contact]

## Contributing

### Code of conduct

Please note that this project is released with a [Code of Conduct][coc].
By participating in this project you agree to abide by its terms.

### Contributing Guidelines

Please read our
[Contributing Guide][contrib]
to see how you can help and give feedback.

## License

Dependente is free and open-source software distributed under the
[MIT License][license].

[pypi]: https://pypi.org/project/dependente/
[conda-forge]: https://github.com/conda-forge/dependente-feedstock
[coverage]: https://app.codecov.io/gh/fatiando/dependente
[license]: https://github.com/fatiando/dependente/blob/main/LICENSE.txt
[contrib]: https://github.com/fatiando/dependente/blob/main/CONTRIBUTING.md
[coc]: https://github.com/fatiando/community/blob/main/CODE_OF_CONDUCT.md
[fatiando]: https://www.fatiando.org
[contact]: https://www.fatiando.org/contact
