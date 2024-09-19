
# item list

List Items in Collection 

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

* `all`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--all`

    Print whole Stac Item



* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    Indent Item Printing



* `bbox`:
    * Type: FLOAT
    * Default: `None`
    * Usage: `-b
--bbox`

    Bounding Box for results: xmax, ymax, xmin, ymin Lon/Lat Coordinates



* `datetime`:
    * Type: STRING
    * Default: `None`
    * Usage: `-d
--datetime`

    Time Range of results. E.g 2018-02-12T00:00:00Z/2018-03-18T12:31:12Z



* `limit`:
    * Type: INT
    * Default: `None`
    * Usage: `-l
--limit`

    Maximum Number of Items to request from API in one call



* `max`:
    * Type: INT
    * Default: `None`
    * Usage: `-m
--max`

    Maximum Number of Items to receive in total



* `assetfilter`:
    * Type: STRING
    * Default: `None`
    * Usage: `-a
--assets`

    Only Print specified assets, assets are separated by ',' 



* `href_only`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-h
--href-only`

    Only Print asset hrefs



* `strip_file`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-s
--strip-file`

    Remove file prefix from asset hrefs



* `outfile`:
    * Type: <click.types.File object at 0x0000028988502840>
    * Default: `<ConsoleStream name='<stdout>' encoding='utf-16-le'>`
    * Usage: `-o
--outfile`

    Write Output to this file



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item list [OPTIONS] COLLECTION_ID

  List Items in Collection

Options:
  --all                   Print whole Stac Item
  -p, --pretty            Indent Item Printing
  -b, --bbox FLOAT...     Bounding Box for results: xmax, ymax, xmin, ymin
                          Lon/Lat Coordinates

  -d, --datetime TEXT     Time Range of results. E.g
                          2018-02-12T00:00:00Z/2018-03-18T12:31:12Z

  -l, --limit INTEGER     Maximum Number of Items to request from API in one
                          call

  -m, --max INTEGER       Maximum Number of Items to receive in total
  -a, --assets TEXT       Only Print specified assets, assets are separated by
                          ','

  -h, --href-only         Only Print asset hrefs
  -s, --strip-file        Remove file prefix from asset hrefs
  -o, --outfile FILENAME  Write Output to this file
  --help                  Show this message and exit.
```

