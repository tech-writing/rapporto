(report-slack)=
# Slack conversations

Produce daily or weekly reports and notifications.

Weekly reports, the most comprehensive ones, are optimized for a happy path
around yielding reports with a _daily granularity_ and an _hourly update_
interval/rate, within a _weekly context_.

## Usage

### Authentication

Please provide a valid GitHub token. This token is invalid.
```shell
export GH_TOKEN="ghp_600VEZtdzinvalid7K2R86JTiKJAAp1wNwVP"
```

Please provide a valid Slack API token. This token is invalid.
```bash
export SLACK_TOKEN="xoxb-your-slack-bot-token"
```
Alternatively to using the environment variable, you can also use the
`rapporto notify --slack-token=` command-line option.

### Options

Note that many CLI options are optional. Just omit them in order to
expand the search scope, or assume reasonable default values.

## Basics

Basic invocations yield reports of type {ref}`github-attention`.

Report and notify about current calendar week.
```shell
rapporto notify --gh-org="acme" --slack-channel="qa-bot" weekly
```

Report and notify about given calendar week.
```shell
rapporto notify --gh-org="acme" --slack-channel="qa-bot" weekly --week="2025W09"
```

For development purposes, zap messages after pressing enter.
```shell
rapporto notify --gh-org="acme" --slack-channel="qa-bot" weekly --zap=key
```

:::{tip}
The command-line option `--gh-org` is a shorthand version of `--github-organization`.
You can use it to save a few keystrokes.
:::

## Advanced

Advanced invocations yield reports of type {ref}`github-attention` and
{ref}`github-actions`, interleaved each day. You will need to supply
a list of repositories for this operation.

Report and notify about current calendar week, loading list of repositories from file.
```shell
rapporto notify \
  --gh-org="acme" \
  --gh-repo="/path/to/repositories.txt" \
  --slack-channel="qa-bot" \
  weekly
```

## Scheduled operations

In order to optimally support scheduled operations, you don't need to supply
the time interval the program should operate on. When invoking it without
`--when`, `--day`, or `--week` options, it will assume reasonable default
values.

Using this incantation style, Rapporto supports a popular use case by running
it unattended and recurrent, for example when hooked into a cron-like scheduler,
providing maximum DWIM convenience to the caller.
