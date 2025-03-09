(report-text)=
# Textual reports

## Usage

### Authentication

Please provide a valid GitHub token. This token is invalid.
```shell
export GH_TOKEN="ghp_600VEZtdzinvalid7K2R86JTiKJAAp1wNwVP"
```

### Options

Note that many CLI options are optional. Just omit them in order to
expand the search scope, or assume reasonable default values.

## Markdown

Report attention items about current day.
```shell
rapporto report --github-organization="acme" daily
```

Report attention items about a given day.
```shell
rapporto report --github-organization="acme" daily --day="2025-02-28"
```

Print yesterday's report.
```shell
rapporto report --github-organization="acme" daily --day="yesterday"
```

Report about current calendar week.
```shell
rapporto report --github-organization="acme" weekly
```

Report about given calendar week.
```shell
rapporto report --github-organization="acme" weekly --day="2025W09"
```

Report attention items and CI failures about a given day.
```shell
rapporto report \
  --github-organization="acme" \
  --github-repository="acme/foobar" \
  daily --day="2025-02-28"
```

Load list of repositories from file.
```shell
rapporto report \
  --github-organization="acme" \
  --github-repository="/path/to/repositories.txt" \
  daily --day="2025-02-28"
```

## YAML

Print today's report in YAML format.
```shell
rapporto report --github-organization="acme" --format="yaml" daily
```
