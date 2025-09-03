---
id: collection
title: collection
description: terrapi command line library documentation -  subcommand
---

# stac collection

Manage STAC Collections.

Collections are groups of related geospatial data items. This command group allows you to:
- List collections.
- Create, update, or delete collections.
- Retrieve metadata for a specific collection.

Examples:
- List collections: `terrapi stac collection list`
- Create a collection: `terrapi stac collection create --file collection.json`
- Delete a collection: `terrapi stac collection delete \<collection_id\>`


## Usage

```
Usage: terrapi stac collection [OPTIONS] COMMAND [ARGS]...
```

## Arguments


## Options

* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac collection [OPTIONS] COMMAND [ARGS]...

  Manage STAC Collections.

  Collections are groups of related geospatial data items. This command group
  allows you to: - List collections. - Create, update, or delete collections.
  - Retrieve metadata for a specific collection.

  Examples: - List collections: `terrapi stac collection list` - Create a
  collection: `terrapi stac collection create --file collection.json` - Delete
  a collection: `terrapi stac collection delete \<collection_id\>`

Options:
  --help  Show this message and exit.

Commands:
  create  Create a new STAC Collection
  delete  Delete a Collection defined by its ID
  get     Get STAC Metadata for a single Collection
  list    List STAC Collections.
  prefix  List all acceptable read/writable prefixes for specific user
  update  Update an existing Collection
```

