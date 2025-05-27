---
id: list
title: list
description: terrapi command line library documentation - slurm subcommand
---

# item list

List STAC Items in a Collection.

    Retrieve and display metadata for items in a specific collection. You can filter items by spatial and temporal properties, or output the full JSON.

    Examples:
    - List all items: `terrapi stac item list <collection_id>`
    - Filter items by bounding box: `terrapi stac item list <collection_id> --bbox -180 -90 180 90`
    - Filter items by time range: `terrapi stac item list <collection_id> --datetime "2020-01-01/2020-12-31"`
    

## Usage

```
Usage: terrapi stac item list [OPTIONS] COLLECTION_ID
```

## Arguments

* `collection_id` (REQUIRED):
    * Type: STRING
    * Default: `None`
    * Usage: `collection_id`


## Options

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
    * Usage: `-a
--all`

    Output the full JSON for each item.



* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    Pretty-print JSON output.



* `outfile`:
    * Type: File
    * Default: `<_io.TextIOWrapper name='<stdout>' encoding='utf-8'>`
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
Usage: terrapi stac item list [OPTIONS] COLLECTION_ID

  List STAC Items in a Collection.

  Retrieve and display metadata for items in a specific collection. You can
  filter items by spatial and temporal properties, or output the full JSON.

  Examples: - List all items: `terrapi stac item list <collection_id>` -
  Filter items by bounding box: `terrapi stac item list <collection_id> --bbox
  -180 -90 180 90` - Filter items by time range: `terrapi stac item list
  <collection_id> --datetime "2020-01-01/2020-12-31"`

Options:
  -b, --bbox FLOAT...     Filter items by bounding box (xmin, ymin, xmax,
                          ymax).
  -d, --datetime TEXT     Filter items by time range (e.g.,
                          2020-01-01/2020-12-31).
  -l, --limit INTEGER     Limit the number of items returned in a single
                          request.
  -m, --max INTEGER       Limit the total number of items returned.
  -a, --all               Output the full JSON for each item.
  -p, --pretty            Pretty-print JSON output.
  -o, --outfile FILENAME  Write output to a file instead of stdout.
  -a, --assets TEXT       Only print specified assets, multiple assets are
                          separated by ','
  -r, --href-only         Only print asset hrefs
  -s, --strip-file        Remove file prefix from asset hrefs
  --help                  Show this message and exit.
```

