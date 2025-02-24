# Options

## Input options

### Time interval

Select time intervals using the `--when=` command-line option,
which uses the [aika] package for parsing.

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


[aika]: https://pypi.org/project/aika/
