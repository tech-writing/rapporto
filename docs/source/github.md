# GitHub Reports

Tap into the GitHub API and generate reports in Markdown format.

## Features

- Actions: Report about CI failures on [GHA].
- Activity: Report about user activity in [PPP] format.
- Attention: Report about bugs and similar important items.

## Setup

For not exhausting the API rate limit too quickly, please use a GitHub
token (classic), that permits access to those scopes:

- `repo`
- `read:org`
- `read:project`

## Usage

### Authentication

Please provide a valid GitHub token. This token is invalid.
```shell
export GH_TOKEN=ghp_600VEZtdzinvalid7K2R86JTiKJAAp1wNwVP
```

### Options

The [`--when`](#when-option) command-line option accepts a wide range of
values to adjust the time interval. You can also omit the option completely,
in which case the program will assume the current day or calendar week.

Note that many other options are also optional. Just omit them in order to
expand the search scope.

### Actions report
Report about activities of GitHub Actions workflow runs, mostly failing ones.
```shell
rapporto github actions --repository=acme/acme-examples
rapporto github actions --repositories-file=acme-repositories.txt
```

### Activity report
Report about activities of individual authors.
```shell
rapporto github activity --organization=python --author=AA-Turner --when="2025-01-01..2025-01-31"
rapporto github activity --organization=python --author=AA-Turner --when="2025W04"
```

### Attention report
Report about important items that deserve your attention, bugs first.
```shell
rapporto github attention --organization=python --when="2025W07"
```
If you want to explore your personal repositories, please use the
`--organization` option with your username, e.g. `--organization=AA-Turner`.

### Backup
Full GitHub project backup using [github-backup].
```shell
rapporto github backup --all --pull-details --prefer-ssh --token="${GH_TOKEN}" --repository=kotori daq-tools
```


[GHA]: https://github.com/features/actions
[github-backup]: https://pypi.org/project/github-backup/
[PPP]: https://weekdone.com/resources/plans-progress-problems
