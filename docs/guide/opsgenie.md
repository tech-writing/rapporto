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
```shell
rapporto opsgenie export-alerts --start-time "12-02-2025T14:00:00" --days 7
```
