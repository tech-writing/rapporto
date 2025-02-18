# Slack Threads

Export Slack threads to Markdown files,
including user mentions, attachments,
and reactions.

## Features

- Resolve Slack user IDs to usernames.
- Export reactions associated with messages.
- Handle attachments and blocks in messages.
- Download and embed file attachments.
- Opsgenie-specific message formatting.
- Comprehensive logging.

## Setup

In order to authenticate with the Slack API, you will need a Slack Bot
authentication token with access permissions to the required [OAuth scopes].

- `channels:read`: To access channel information.
- `channels:history`: To read message history in channels.
- `groups:read`: To access private channels information.
- `groups:history`: To read message history in private channels.
- `users:read`: To resolve user IDs to usernames.
- `files:read`: To download file attachments.
- `reactions:read`: To access reactions on messages.

## Usage

### Export thread

Either define the authentication token as an environment variable,
```bash
export SLACK_TOKEN='xoxb-your-slack-bot-token'
```
or use the `--slack-token` command-line option.

Export Slack thread into Markdown.
```shell
rapporto slack export https://acme.slack.com/archives/D018V8WDABA/p1738873838427919
```


[OAuth scopes]: https://api.slack.com/authentication/oauth-v2#scopes
