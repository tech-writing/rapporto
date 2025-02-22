# Slack UI

Have conversations on Slack.

## Overview

- Use threaded conversations on Slack like a static documentation generator,
  producing idempotent message content, even when spanning multiple messages.

- Slack understands a Markdown-like syntax called `mrkdwn`, and a layout language based
  on block elements, which includes a rich-text element.
  This program however exclusively focuses on letting the user use standard Markdown. 

## Synopsis

Send a message to a channel, using either the channel name, id, or URL.
```shell
rapporto slack send --channel=sig-automation-testdrive --message="**Hello, world.**"
```
```shell
rapporto slack send --channel=C08EF2NGZGB --message="**Hello, world.**"
```
```shell
rapporto slack send --channel=https://acme.slack.com/archives/C08EF2NGZGB --message="**Hello, world.**"
```

## Features

### Multiple messages

Send multiple messages at once.
```shell
rapporto slack send --channel=C08EF2NGZGB --message="**Hello**" --message="**world**"
```

### Zap

Send a probing message, and zap it again after pressing enter.
```shell
rapporto slack send --channel=C08EF2NGZGB --message="**Hello, world.**" --zap=key
```

Send a probing message, and zap it again after three seconds.
```shell
rapporto slack send --channel=C08EF2NGZGB --message="**Hello, world.**" --zap=3s
```

### Update

Update an existing message by message ID.
```shell
rapporto slack send --channel=C08EF2NGZGB --update=1740421792.358899 --message='_???_'
```

Update an existing message by URL.
```shell
rapporto slack send --update=https://acme.slack.com/archives/C08EF2NGZGB/p1740421792358899 --message='_!!!_'
```

### I/O

Send a message, reading its content from stdin.
```shell
echo -e "**Question:** What is...?\n**Answer:** _42_" | \
  rapporto slack send --channel=C08EF2NGZGB --message=- 
```

Update an existing message, reading its content from a file.
```shell
rapporto slack send --channel=C08EF2NGZGB --update=1740421792.358899 --message=2025-02-28.md 
```

### Reply

Reply to a specific message by message ID.
```shell
rapporto slack send --channel=C08EF2NGZGB --reply-to=1740421750.904349 --message=hello
```

Reply to a specific message by URL.
```shell
rapporto slack send --reply-to=https://acme.slack.com/archives/C08EF2NGZGB/p1740421792358899 --message=hello
```

### Delete

Delete a specific message by message ID.
```shell
rapporto slack delete --channel=C08EF2NGZGB --id=1740437309.683889
```

Delete a specific message by URL.
```shell
rapporto slack delete --id=https://acme.slack.com/archives/C08EF2NGZGB/p1740789929143349
```
