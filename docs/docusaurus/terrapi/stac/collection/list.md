---
id: list
title: list
description: terrapi command line library documentation - collection subcommand
---

# collection list

List STAC Collections.

Retrieve and display metadata for all available STAC collections. You can filter collections by ID, include additional metadata fields, or output the full JSON.

Examples:
- List all collections: `terrapi stac collection list`
- Filter collections by ID: `terrapi stac collection list --filter "landsat.*"`
- Output full JSON: `terrapi stac collection list --all`


## Usage

```
Usage: terrapi stac collection list [OPTIONS]
```

## Arguments


## Options

* `filter`:
    * Type: STRING
    * Default: ``
    * Usage: `-f
--filter`

    Filter collections by ID using a regular expression.



* `title`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-t
--title`

    Include collection titles in the output.



* `description`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-d
--description`

    Include collection descriptions in the output.



* `all`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-a
--all`

    Output the full JSON for each collection.



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
Usage: terrapi stac collection list [OPTIONS]

  List STAC Collections.

  Retrieve and display metadata for all available STAC collections. You can
  filter collections by ID, include additional metadata fields, or output the
  full JSON.

  Examples: - List all collections: `terrapi stac collection list` - Filter
  collections by ID: `terrapi stac collection list --filter "landsat.*"` -
  Output full JSON: `terrapi stac collection list --all`

Options:
  -f, --filter TEXT       Filter collections by ID using a regular expression.
  -t, --title             Include collection titles in the output.
  -d, --description       Include collection descriptions in the output.
  -a, --all               Output the full JSON for each collection.
  -p, --pretty            Pretty-print JSON output.
  -o, --outfile FILENAME  Write output to a file instead of stdout.
  --help                  Show this message and exit.
```

