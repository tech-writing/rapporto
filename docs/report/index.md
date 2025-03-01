# Reports

Daily reports and notifications, using a weekly context and a hourly
granularity, fluently converging to Slack conversations, at your disposal.


## Usage

The reporting section includes two subsystems. Both produce reports about
a given time interval.

:`rapporto report`: Produce reports in Markdown or YAML formats. 
:`rapporto notify`: Produce reports and submit to Slack conversation.

:::{tip}
In the examples below, you can also omit the `--when` option completely.
In this case, the current day or week will be assumed.
:::

### Authentication

Please provide a valid GitHub token. This token is invalid.
```shell
export GH_TOKEN=ghp_600VEZtdzinvalid7K2R86JTiKJAAp1wNwVP
```

Please provide a valid Slack API token. This token is invalid.
```bash
export SLACK_TOKEN='xoxb-your-slack-bot-token'
```
Alternatively to using the environment variable, you can also use the
`rapporto notify --slack-token=` command-line option.


## Reports

Report about given day.
```shell
rapporto report --github-organization=acme daily --when=2025-02-28
```

Report about given week.
```shell
rapporto report --github-organization=acme weekly --when=2025W09
```


## Conversations

Report and notify about current calendar week.
```shell
rapporto notify --slack-channel="janitor-bot" weekly
```

Report and notify about given calendar week.
```shell
rapporto notify --slack-channel="janitor-bot" weekly --week=2025W09
```

For development purposes, zap messages after pressing enter.
```shell
rapporto notify --slack-channel="janitor-bot" weekly --zap=key
```
