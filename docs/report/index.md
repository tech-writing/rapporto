# Reports

Produce daily reports and notifications, using a weekly context and an hourly
granularity, fluently converging into Slack conversations, at your disposal.

## Overview

The reporting section includes two subsystems. Both produce reports about
a given time interval.

:`rapporto report`: Produce reports in Markdown or YAML format.
:`rapporto notify`: Produce reports and submit to Slack conversation.

> I am currently producing Markdown with Rapporto, similar to how you would
> use a [static site generator] like a traditional tool in tech-writing,
> for example Docusaurus, Hugo, Jekyll, MkDocs, Sphinx, or [many others].
>
> Contrary to a generator that produces HTML output,
> Rapporto does not render Markdown or reStructuredText into HTML, which
> is then displayed in the browser. Instead, information is acquired from
> API calls, converted into Markdown, then displayed, for example, on Slack.
 
> Using Rapporto to drive threaded conversations on Slack tries to behave
> like a static site generator, producing idempotent message content, even
> when spanning multiple messages.

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

The [`--when`](#when-option) command-line option accepts a wide range of
values to adjust the time interval. You can also omit the option completely,
in which case the program will assume the current day or calendar week.

## Markdown Reports

Report about given day.
```shell
rapporto report --github-organization="acme" daily --when="2025-02-28"
```

Report about given calendar week.
```shell
rapporto report --github-organization="acme" weekly --when="2025W09"
```

Print yesterday's report.
```shell
rapporto report --github-organization="acme" daily --when="yesterday"
```

Print today's report in YAML format.
```shell
rapporto report --github-organization="acme" --format="yaml" daily
```


## Slack Conversations

Report and notify about current calendar week.
```shell
rapporto notify --gh-org="acme" --slack-channel="janitor-bot" weekly
```

Report and notify about given calendar week.
```shell
rapporto notify --gh-org="acme" --slack-channel="janitor-bot" weekly --week="2025W09"
```

For development purposes, zap messages after pressing enter.
```shell
rapporto notify --gh-org="acme" --slack-channel="janitor-bot" weekly --zap=key
```

:::{tip}
The command-line option `--gh-org` is a shorthand version of `--github-organization`.
You can use it to save a few keystrokes.
:::


[many others]: https://github.com/myles/awesome-static-generators
[static site generator]: https://en.wikipedia.org/wiki/Static_site_generator
