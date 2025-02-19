# GitHub Reports

Tap into the GitHub API and generate reports in Markdown format.

## Features

- Report about user activity in [PPP] format.
- Report about CI failures on [GHA].
- Report about bugs and similar important items.

## Setup

For not exhausting the API rate limit too quickly, please use a GitHub
token (classic), that permits access to those scopes:

- `repo`
- `read:org`
- `read:project`

## Usage

### Introduction

Please provide a valid GitHub token. This token is invalid.
```shell
export GH_TOKEN=ghp_600VEZtdzinvalid7K2R86JTiKJAAp1wNwVP
```

Note that many options are optional. Just omit them in order to expand the
search scope.

### PPP reports
Report about activities of individual authors.
```shell
rapporto gh ppp --organization=python --author=AA-Turner --timerange="2025-01-01..2025-01-31"
rapporto gh ppp --organization=python --author=AA-Turner --timerange="2025W04"
```

### CI reports
Report about activities of GitHub Actions workflow runs, mostly failing ones.
```shell
rapporto gh ci --repository=acme/acme-examples
rapporto gh ci --repositories-file=acme-repositories.txt
```

### Importance reports
Report about important items that deserve your attention, bugs first.
```shell
rapporto gh att --organization=python --timerange="2025W07"
```
If you want to explore your personal repositories, please use the
`--organization` option with your username, e.g. `--organization=AA-Turner`.


[GHA]: https://github.com/features/actions
[PPP]: https://weekdone.com/resources/plans-progress-problems
