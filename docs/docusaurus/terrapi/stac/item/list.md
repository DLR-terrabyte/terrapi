---
id: list
title: list
description: terrapi command line library documentation - slurm subcommand
---

# item list

 List STAC Items in a specific Collection 
    
    The items can be filtered by time and space.
      It is also possible to specify spefic assets as well as only printing the path to the assets. 
      This allows the creation of a file list for processing in not stac aware applications 
    

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

    Print whole STAC Item



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

    Only print specified assets, multiple assets are separated by ',' 



* `href_only`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-h
--href-only`

    Only print asset hrefs



* `strip_file`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-s
--strip-file`

    Remove file prefix from asset hrefs



* `outfile`:
    * Type: File
    * Default: `stdout`
    * Usage: `-o
--outfile`

    Write Results to this file



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item list [OPTIONS] COLLECTION_ID

  List STAC Items in a specific Collection

  The items can be filtered by time and space.   It is also possible to
  specify spefic assets as well as only printing the path to the assets.
  This allows the creation of a file list for processing in not stac aware
  applications

Options:
  --all                   Print whole STAC Item
  -p, --pretty            Indent Item Printing
  -b, --bbox FLOAT...     Bounding Box for results: xmax, ymax, xmin, ymin
                          Lon/Lat Coordinates
  -d, --datetime TEXT     Time Range of results. E.g
                          2018-02-12T00:00:00Z/2018-03-18T12:31:12Z
  -l, --limit INTEGER     Maximum Number of Items to request from API in one
                          call
  -m, --max INTEGER       Maximum Number of Items to receive in total
  -a, --assets TEXT       Only print specified assets, multiple assets are
                          separated by ','
  -h, --href-only         Only print asset hrefs
  -s, --strip-file        Remove file prefix from asset hrefs
  -o, --outfile FILENAME  Write Results to this file
  --help                  Show this message and exit.
```

