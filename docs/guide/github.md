# GitHub Reports

## Setup

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
