# Goofing on Slack

Have conversations on Slack, and stick to them.

## Features

:Operations:
    `goof slack` supports fundamental send, update, and delete operations
    on messages, and threaded conversations.

:Polyglot:
    `goof slack` accepts different types of values to address channels and
    messages: Channel names, message identifiers (timestamps), and full URLs
    to both.

:Multiple Messages:
    Send and delete multiple messages within a single operation,
    increasing convenience and throughput.

:Message Zapping:
    Using the `--zap=` command-line option, messages are removed again after
    receiving corresponding events, making the feature suitable for development
    and debugging purposes.

:Standard Markdown:
    Slack understands `plain_text`, a Markdown-like syntax called [`mrkdwn`],
    and [Block Kit], a layout system based on blocks and block elements, which
    also includes a [rich text] block element.
    Because [mrkdwn is proprietary], and block elements don't exactly fit into
    command-line paradigms, this program exclusively focuses on letting
    users use [Standard Markdown]. 

## Synopsis

Send a message to a Slack channel, using Markdown format.
```shell
goof slack send --channel="testdrive" --message="**Hello, world.**"
```

## Usage

Either define the authentication token as an environment variable,
```bash
export SLACK_TOKEN='xoxb-your-slack-bot-token'
```
or use the `--slack-token` command-line option.

### Send

Send a message to a channel, using either the channel name, id, or URL.
```shell
goof slack send --channel="sig-automation-testdrive" --message="**Hello, world.**"
```
```shell
goof slack send --channel="C08EF2NGZGB" --message="**Hello, world.**"
```
```shell
goof slack send \
  --channel="https://acme.slack.com/archives/C08EF2NGZGB" \
  --message="**Hello, world.**"
```

### Multiple messages

Send multiple messages at once.
```shell
goof slack send --channel="C08EF2NGZGB" --message="**Hello**" --message="**world**"
```

### Update

Update an existing message by message ID.
```shell
goof slack send \
  --channel="C08EF2NGZGB" \
  --update="1740421792.358899" \
  --message='_???_'
```

Update an existing message by URL.
```shell
goof slack send \
  --update="https://acme.slack.com/archives/C08EF2NGZGB/p1740421792358899" \
  --message='_!!!_'
```

### I/O

Send a message, reading its content from stdin.
```shell
echo -e "**Question:** What is...?\n**Answer:** _42_" | \
  goof slack send --channel="C08EF2NGZGB" --message=- 
```

Update an existing message, reading its content from a file.
```shell
goof slack send \
  --channel="C08EF2NGZGB" \
  --update="1740421792.358899" \
  --message="2025-02-28.md" 
```

### Reply

Reply to a specific message by message ID.
```shell
goof slack send \
  --channel="C08EF2NGZGB" \
  --reply-to="1740421750.904349" \
  --message="hello"
```

Reply to a specific message by URL.
```shell
goof slack send \
  --reply-to="https://acme.slack.com/archives/C08EF2NGZGB/p1740421792358899" \
  --message="hello"
```

### Delete

Delete a specific message by message ID.
```shell
goof slack delete --channel="C08EF2NGZGB" --id="1740437309.683889"
```

Delete a specific message by URL.
```shell
goof slack delete --id="https://acme.slack.com/archives/C08EF2NGZGB/p1740789929143349"
```

### Zap

Send a probing message, and zap it again after pressing enter.
```shell
goof slack send --channel="C08EF2NGZGB" --message="**Hello, world.**" --zap=key
```

Send a probing message, and zap it again after three seconds.
```shell
goof slack send --channel="C08EF2NGZGB" --message="**Hello, world.**" --zap=3s
```


[Block Kit]: https://api.slack.com/reference/block-kit
[`mrkdwn`]: https://api.slack.com/reference/surfaces/formatting#basic-formatting
[mrkdwn is proprietary]: https://xkcd.com/927/
[rich text]: https://api.slack.com/reference/block-kit/blocks#rich_text
[Standard Markdown]: https://daringfireball.net/projects/markdown/
