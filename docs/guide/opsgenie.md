# Opsgenie Reports

Tap into the Opsgenie API and generate alert reports in Markdown format.

## Features

- CLI interface
- Query builder
- Markdown or plaintext output

## Setup

In order to authenticate with the Opsgenie API, you will need an Opsgenie API key.

## Usage

Either define the authentication token as an environment variable,
```bash
export OPSGENIE_API_KEY="your-api-key"
```
or use the `--api-key` command-line option.

### Alert report

Generate report about Opsgenie alerts.

Report about the previous seven days.
```shell
rapporto opsgenie export-alerts --when="-7d"
```

Report about yesterday.
```shell
rapporto opsgenie export-alerts --when="yesterday"
```

Report about the previous week.
```shell
rapporto opsgenie export-alerts --when="last week"
```

Report about the current week.
```shell
rapporto opsgenie export-alerts --when="this week"
```

Describe the time interval by start time and duration in days.
```shell
rapporto opsgenie export-alerts --start-time "12-02-2025T14:00:00" --days 7
```
