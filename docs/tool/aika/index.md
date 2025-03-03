(when-option)=

# Aika

You can conveniently select time intervals using the `--when=` command-line
option, supported by [Aika]. 

## Features

You can use absolute calendar notations,

- Week: `2025W01`
- Month: `2025M02`, `2025-02`
- Quarter: `2025Q03`
- Year: `2025`

relative time delta notations,
- Day: `-1d`, `-1 day`
- Week: `-1w`, `-1 week`
- Month: `-1M`, `-1 month`
- Year: `-1y`, `-1 year`
- Quarter: `-3M`, `-3 months`
- Mixed: `-3d3h5m30s`

or relative human-readable notations. 
- now
- today
- last week
- this week
- last month
- this month

## Synopsis

### API
```python
>>> from aika import TimeIntervalParser
>>> 
>>> ti = TimeIntervalParser()
>>>
>>> ti.parse("Sat - Tue")
>>> (dt.datetime(2023, 8, 26, 0, 0), dt.datetime(2023, 8, 29, 23, 59, 59, 999999))
```

### CLI
:::{todo}
Add CLI interface.
:::


## Examples

Report about the previous seven days.
```shell
rapporto <anything> --when="-7d"
```

Report about yesterday.
```shell
rapporto <anything> --when="yesterday"
```

Report about the previous week.
```shell
rapporto <anything> --when="last week"
```

Report about the current week.
```shell
rapporto <anything> --when="this week"
```


[Aika]: https://pypi.org/project/aika/
[DWIM]: https://en.wikipedia.org/wiki/DWIM
