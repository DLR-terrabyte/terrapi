---
id: delete
title: delete
description: terrapi command line library documentation - collection subcommand
---

# collection delete

Delete a Collection defined by its ID

This will permanently delete the specified collection with all its Items from the private STAC Catalogue. 


## Usage

```
Usage: terrapi stac collection delete [OPTIONS] COLLECTION_ID
```

## Arguments

* `collection_id` (REQUIRED):
    * Type: STRING
    * Default: `None`
    * Usage: `collection_id`


## Options

* `yes`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--yes`

    Confirm deletion.



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac collection delete [OPTIONS] COLLECTION_ID

  Delete a Collection defined by its ID

  This will permanently delete the specified collection with all its Items
  from the private STAC Catalogue.

Options:
  --yes   Confirm deletion.
  --help  Show this message and exit.
```

