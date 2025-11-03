---
id: queryables
title: queryables
description: terrapi command line library documentation - item subcommand
---

# item queryables

Get queryable attributes for items in a collection.

Retrieves the schema of queryable attributes that can be used for filtering items
in the specified collection using CQL2 expressions.

Examples:
- Get queryables: `terrapi stac item queryables \<collection_id\>`
- Pretty print: `terrapi stac item queryables \<collection_id\> --pretty`


## Usage

```
Usage: terrapi stac item queryables [OPTIONS] COLLECTION_ID
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

    Pretty-print JSON output.



* `outfile`:
    * Type: File
    * Default: `\<_NonClosingTextIOWrapper name='\<stdout\>' encoding='utf-8'\>`
    * Usage: `-o
--outfile`

    Write output to a file instead of stdout.



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item queryables [OPTIONS] COLLECTION_ID

  Get queryable attributes for items in a collection.

  Retrieves the schema of queryable attributes that can be used for filtering
  items in the specified collection using CQL2 expressions.

  Examples: - Get queryables: `terrapi stac item queryables \<collection_id\>` -
  Pretty print: `terrapi stac item queryables \<collection_id\> --pretty`

Options:
  -p, --pretty            Pretty-print JSON output.
  -o, --outfile FILENAME  Write output to a file instead of stdout.
  --help                  Show this message and exit.
```

