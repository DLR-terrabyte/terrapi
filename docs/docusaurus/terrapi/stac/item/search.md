---
id: search
title: search
description: terrapi command line library documentation - item subcommand
---

# item search

Search STAC Items across collections.

Search for items using various filters including spatial, temporal, and custom expressions.
The search endpoint allows querying across multiple collections at once.

Examples:
- Search all items: `terrapi stac item search`
- Filter by collection: `terrapi stac item search --collection landsat-c2-l2`
- Filter by bbox: `terrapi stac item search --bbox -180 -90 180 90`
- Filter by time: `terrapi stac item search --datetime "2020-01-01/2020-12-31"`
- Use CQL2 filter: `terrapi stac item search --filter "eo:cloud_cover \< 10"`


## Usage

```
Usage: terrapi stac item search [OPTIONS]
```

## Arguments


## Options

* `collections`:
    * Type: STRING
    * Default: `None`
    * Usage: `-c
--collection`

    Filter by collection ID(s). Separate multiple IDs with ','



* `bbox`:
    * Type: FLOAT
    * Default: `None`
    * Usage: `-b
--bbox`

    Filter items by bounding box (xmin, ymin, xmax, ymax).



* `datetime`:
    * Type: STRING
    * Default: `None`
    * Usage: `-d
--datetime`

    Filter items by time range (e.g., 2020-01-01/2020-12-31).



* `filter_expr`:
    * Type: STRING
    * Default: `None`
    * Usage: `-f
--filter`

    CQL2-text filter expression.



* `limit`:
    * Type: INT
    * Default: `None`
    * Usage: `-l
--limit`

    Limit the number of items returned in a single request.



* `max`:
    * Type: INT
    * Default: `None`
    * Usage: `-m
--max`

    Limit the total number of items returned.



* `all`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--all`

    Output the full JSON for each item.



* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    Pretty-print JSON output.



* `outfile`:
    * Type: File
    * Default: `\<_NonClosingTextIOWrapper name='\<stdout\>' encoding='utf-8'\>`
    * Usage: `-o
--outfile`

    Write output to a file instead of stdout.



* `assetfilter`:
    * Type: STRING
    * Default: `None`
    * Usage: `-a
--assets`

    Only print specified assets, multiple assets are separated by ','



* `href_only`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-r
--href-only`

    Only print asset hrefs



* `strip_file`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-s
--strip-file`

    Remove file prefix from asset hrefs



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item search [OPTIONS]

  Search STAC Items across collections.

  Search for items using various filters including spatial, temporal, and
  custom expressions. The search endpoint allows querying across multiple
  collections at once.

  Examples: - Search all items: `terrapi stac item search` - Filter by
  collection: `terrapi stac item search --collection landsat-c2-l2` - Filter
  by bbox: `terrapi stac item search --bbox -180 -90 180 90` - Filter by time:
  `terrapi stac item search --datetime "2020-01-01/2020-12-31"` - Use CQL2
  filter: `terrapi stac item search --filter "eo:cloud_cover \< 10"`

Options:
  -c, --collection TEXT   Filter by collection ID(s). Separate multiple IDs
                          with ','
  -b, --bbox FLOAT...     Filter items by bounding box (xmin, ymin, xmax,
                          ymax).
  -d, --datetime TEXT     Filter items by time range (e.g.,
                          2020-01-01/2020-12-31).
  -f, --filter TEXT       CQL2-text filter expression.
  -l, --limit INTEGER     Limit the number of items returned in a single
                          request.
  -m, --max INTEGER       Limit the total number of items returned.
  --all                   Output the full JSON for each item.
  -p, --pretty            Pretty-print JSON output.
  -o, --outfile FILENAME  Write output to a file instead of stdout.
  -a, --assets TEXT       Only print specified assets, multiple assets are
                          separated by ','
  -r, --href-only         Only print asset hrefs
  -s, --strip-file        Remove file prefix from asset hrefs
  --help                  Show this message and exit.
```

