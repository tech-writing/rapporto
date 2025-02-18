# GitHub Reports

Tap into the GitHub API and generate reports in Markdown format.

## Features

- Report about user activity in [PPP] format.
- Report about CI failures on [GHA].

## Setup

For not exhausting the API rate limit too quickly, please use a GitHub
token (classic), that permits access to those scopes:

- `repo:status`
- `read:org`
- `read:project`

## Usage

Please provide a valid GitHub token. This token is invalid.
```shell
export GH_TOKEN=ghp_600VEZtdzinvalid7K2R86JTiKJAAp1wNwVP
```

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


[GHA]: https://github.com/features/actions
[PPP]: https://weekdone.com/resources/plans-progress-problems
