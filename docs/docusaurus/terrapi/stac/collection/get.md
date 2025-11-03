---
id: get
title: get
description: terrapi command line library documentation - collection subcommand
---

# collection get

Get STAC Metadata for a single Collection 

It requires the Collection ID as an Argument


## Usage

```
Usage: terrapi stac collection get [OPTIONS] COLLECTION_ID
```

## Arguments

* `collection_id` (REQUIRED):
    * Type: STRING
    * Default: `Sentinel.UNSET`
    * Usage: `collection_id`


## Options

* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    print pretty readable json



* `outfile`:
    * Type: File
    * Default: `\<_NonClosingTextIOWrapper name='\<stdout\>' encoding='utf-8'\>`
    * Usage: `-o
--outfile`

    Output file.



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac collection get [OPTIONS] COLLECTION_ID

  Get STAC Metadata for a single Collection

  It requires the Collection ID as an Argument

Options:
  -p, --pretty            print pretty readable json
  -o, --outfile FILENAME  Output file.
  --help                  Show this message and exit.
```

