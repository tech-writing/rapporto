# Rapporto

A program for harvesting information from GitHub.

» [Documentation]
| [Changelog]
| [PyPI]
| [Issues]
| [Source code]
| [License]
| [Community Forum]

[![Release Notes][badge-release-notes]][project-release-notes]
[![CI][badge-ci]][project-ci]
[![Downloads per month][badge-downloads-per-month]][project-downloads]

[![Package version][badge-package-version]][project-pypi]
[![License][badge-license]][project-license]
[![Status][badge-status]][project-pypi]
[![Supported Python versions][badge-python-versions]][project-pypi]

## Setup

Install package from PyPI.
```shell
{apt,brew,pip,zypper} install uv
```
```shell
uv tool install --upgrade rapporto
```

For not exhausting the API rate limit too quickly, please provide a valid
GitHub token that minimally permits access to the scopes `repo:status`,
`read:org`, and `read:project`. This token is invalid.
```shell
export GH_TOKEN=ghp_600VEZtdzinvalid7K2R86JTiKJAAp1wNwVP
```

## Usage

### PPP reports
Report about activities of individual authors.
```shell
rapporto gh ppp --organization=python --author=AA-Turner --timerange="2025-01-01..2025-01-31"
rapporto gh ppp --organization=python --author=AA-Turner --timerange="2025W04"
```

### QA/CI reports
Report about activities of GitHub Actions workflow runs.
```shell
rapporto gh qa --repository=acme/acme-examples
rapporto gh qa --repositories-file=acme-repositories.txt
```

## Notes

For soft-installing Rapporto from GitHub, use this alias.
```shell
alias rapporto="uv run --with 'rapporto @ https://github.com/tech-writing/rapporto/archive/refs/heads/main.zip' rapporto"
```

## Prior art
- https://github.com/saschpe/rapport
- https://github.com/nedbat/dinghy
- https://github.com/kneth/gh-utils
- https://github.com/slackapi/slack-github-action
- Many more.


[Changelog]: https://github.com/tech-writing/rapporto/blob/main/CHANGES.md
[Community Forum]: https://community.panodata.org/
[Documentation]: https://rapporto.readthedocs.io/
[Issues]: https://github.com/tech-writing/rapporto/issues
[License]: https://github.com/tech-writing/rapporto/blob/main/LICENSE
[managed on GitHub]: https://github.com/tech-writing/rapporto
[PyPI]: https://pypi.org/project/rapporto/
[Source code]: https://github.com/tech-writing/rapporto

[badge-ci]: https://github.com/tech-writing/rapporto/actions/workflows/main.yml/badge.svg
[badge-downloads-per-month]: https://pepy.tech/badge/rapporto/month
[badge-license]: https://img.shields.io/github/license/tech-writing/rapporto.svg
[badge-package-version]: https://img.shields.io/pypi/v/rapporto.svg
[badge-python-versions]: https://img.shields.io/pypi/pyversions/rapporto.svg
[badge-release-notes]: https://img.shields.io/github/release/tech-writing/rapporto?label=Release+Notes
[badge-status]: https://img.shields.io/pypi/status/rapporto.svg
[project-ci]: https://github.com/tech-writing/rapporto/actions/workflows/main.yml
[project-downloads]: https://pepy.tech/project/rapporto/
[project-license]: https://github.com/tech-writing/rapporto/blob/main/LICENSE
[project-pypi]: https://pypi.org/project/rapporto
[project-release-notes]: https://github.com/tech-writing/rapporto/releases
