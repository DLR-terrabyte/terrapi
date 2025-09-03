---
id: validate
title: validate
description: terrapi command line library documentation - item subcommand
---

# item validate

Validate a STAC Item.

This command validates the structure and content of a STAC Item against the STAC specification.
The `validate_stac_item` function ensures that the provided item adheres to the required schema and standards.


## Usage

```
Usage: terrapi stac item validate [OPTIONS]
```

## Arguments


## Options

* `collection_id`:
    * Type: STRING
    * Default: `None`
    * Usage: `-c`

    ID of the Collection. If specified will overwrite the ID in the Item JSON



* `item_id`:
    * Type: STRING
    * Default: `None`
    * Usage: `-i`

    ID of the Item. If specified will overwrite the ID in the Item JSON



* `inputfile`:
    * Type: File
    * Default: `None`
    * Usage: `-f
--file`

    Read Item JSON from File. Specify - to read from pipe



* `json_str`:
    * Type: STRING
    * Default: `None`
    * Usage: `-j
--json`

    Provide item as JSON String



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item validate [OPTIONS]

  Validate a STAC Item.

  This command validates the structure and content of a STAC Item against the
  STAC specification. The `validate_stac_item` function ensures that the
  provided item adheres to the required schema and standards.

Options:
  -c TEXT              ID of the Collection. If specified will overwrite the
                       ID in the Item JSON
  -i TEXT              ID of the Item. If specified will overwrite the ID in
                       the Item JSON
  -f, --file FILENAME  Read Item JSON from File. Specify - to read from pipe
  -j, --json TEXT      Provide item as JSON String
  --help               Show this message and exit.
```

