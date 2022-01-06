# Dependente: Inspect Python package dependencies

Part of the [Fatiando a Terra][fatiando] project

[![Latest release on PyPI](https://img.shields.io/pypi/v/dependente.svg?style=flat-square)][pypi]
[![Latest release on conda-forge](https://img.shields.io/conda/vn/conda-forge/dependente.svg?style=flat-square)][conda-forge]
[![Compatible Python versions](https://img.shields.io/pypi/pyversions/dependente.svg?style=flat-square)][pypi]

## About

*Dependente* is a small command-line program for extracting 
dependencies from Python project files (`pyproject.toml` and `setup.cfg`)
and converting them into `requirements.txt`-type files for use with
`pip` and `conda`.

The main reason to do so is to control and customize the testing 
environment on continuous integration (CI) while avoiding repeting 
the list of dependencies in multiple places.

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

Use the command

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
[license]: https://github.com/fatiando/dependente/blob/main/LICENSE.txt
[contrib]: https://github.com/fatiando/dependente/blob/main/CONTRIBUTING.md
[coc]: https://github.com/fatiando/community/blob/main/CODE_OF_CONDUCT.md
[fatiando]: https://www.fatiando.org
[contact]: https://www.fatiando.org/contact
