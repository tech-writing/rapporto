# Reports

Produce daily reports and notifications, using a weekly context and an hourly
granularity, fluently converging into Slack conversations, at your disposal.

```{toctree}
:maxdepth: 1
:hidden:

text
slack
```

## Overview

The reporting section includes different subsystems. All of them have in
common to produce reports about a given time interval.

:{ref}`rapporto report <report-text>`: Produce reports in Markdown or YAML format.
:{ref}`rapporto notify <report-slack>`: Produce reports and submit them to Slack conversations.

> Producing Markdown with Rapporto feels similar to how you would
> use a [static site generator] like a traditional tool in tech-writing,
> for example Docusaurus, Hugo, Jekyll, MkDocs, Sphinx, and [many others].
>
> Contrary to a generator that produces HTML output,
> Rapporto does not render Markdown or reStructuredText into HTML, which
> is then displayed in the browser. Instead, information is acquired from
> API calls, converted into Markdown, then displayed, for example, on Slack.


[many others]: https://github.com/myles/awesome-static-generators
[static site generator]: https://en.wikipedia.org/wiki/Static_site_generator
