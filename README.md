# Rapporto

A program for harvesting information from GitHub and Slack.

» [Documentation]
| [Changelog]
| [PyPI]
| [Issues]
| [Source code]
| [License]
| [Community Forum]

[![Release Notes][badge-release-notes]][project-release-notes]
[![CI][badge-ci]][project-ci]
[![Coverage][badge-coverage]][project-coverage]
[![Downloads per month][badge-downloads-per-month]][project-downloads]

[![Package version][badge-package-version]][project-pypi]
[![License][badge-license]][project-license]
[![Status][badge-status]][project-pypi]
[![Supported Python versions][badge-python-versions]][project-pypi]

## Installation

We recommend to use the [uv] package manager.
```shell
{apt,brew,pip,zypper} install uv
```

### Persistent

Install package from PyPI as a [tool].
```shell
uv tool install --upgrade rapporto
```

### Ephemeral

Soft-install package from GitHub.
```shell
alias rapporto="uvx --with 'rapporto @ https://github.com/tech-writing/rapporto/archive/refs/heads/main.zip' -- rapporto"
```

## Usage

See [Rapporto User Guide].


[Changelog]: https://github.com/tech-writing/rapporto/blob/main/CHANGES.md
[Community Forum]: https://community.panodata.org/
[Documentation]: https://rapporto.readthedocs.io/
[Issues]: https://github.com/tech-writing/rapporto/issues
[License]: https://github.com/tech-writing/rapporto/blob/main/LICENSE
[managed on GitHub]: https://github.com/tech-writing/rapporto
[PyPI]: https://pypi.org/project/rapporto/
[Rapporto User Guide]: https://rapporto.readthedocs.io/guide/
[Source code]: https://github.com/tech-writing/rapporto
[tool]: https://docs.astral.sh/uv/guides/tools/
[uv]: https://docs.astral.sh/uv/

[badge-ci]: https://github.com/tech-writing/rapporto/actions/workflows/main.yml/badge.svg
[badge-coverage]: https://codecov.io/gh/tech-writing/rapporto/branch/main/graph/badge.svg
[badge-downloads-per-month]: https://pepy.tech/badge/rapporto/month
[badge-license]: https://img.shields.io/github/license/tech-writing/rapporto.svg
[badge-package-version]: https://img.shields.io/pypi/v/rapporto.svg
[badge-python-versions]: https://img.shields.io/pypi/pyversions/rapporto.svg
[badge-release-notes]: https://img.shields.io/github/release/tech-writing/rapporto?label=Release+Notes
[badge-status]: https://img.shields.io/pypi/status/rapporto.svg
[project-ci]: https://github.com/tech-writing/rapporto/actions/workflows/main.yml
[project-coverage]: https://app.codecov.io/gh/tech-writing/rapporto
[project-downloads]: https://pepy.tech/project/rapporto/
[project-license]: https://github.com/tech-writing/rapporto/blob/main/LICENSE
[project-pypi]: https://pypi.org/project/rapporto
[project-release-notes]: https://github.com/tech-writing/rapporto/releases
