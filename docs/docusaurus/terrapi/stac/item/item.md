---
id: item
title: item
description: terrapi command line library documentation -  subcommand
---

# stac item

Manage STAC Items.

Items are individual geospatial data records within a collection. This command group allows you to:
- List items in a collection.
- Create, update, or delete items.
- Retrieve metadata for a specific item.

Examples:
- List items: `terrapi stac item list \<collection_id\>`
- Create an item: `terrapi stac item create \<collection_id\> --file item.json`
- Delete an item: `terrapi stac item delete \<collection_id\> \<item_id\>`


## Usage

```
Usage: terrapi stac item [OPTIONS] COMMAND [ARGS]...
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
Usage: terrapi stac item [OPTIONS] COMMAND [ARGS]...

  Manage STAC Items.

  Items are individual geospatial data records within a collection. This
  command group allows you to: - List items in a collection. - Create, update,
  or delete items. - Retrieve metadata for a specific item.

  Examples: - List items: `terrapi stac item list \<collection_id\>` - Create an
  item: `terrapi stac item create \<collection_id\> --file item.json` - Delete
  an item: `terrapi stac item delete \<collection_id\> \<item_id\>`

Options:
  --help  Show this message and exit.

Commands:
  create      Create new Item(s) in specified Collection
  delete      Delete an Item from Collection
  get         Retrieve metadata for a single STAC item.
  list        List STAC Items in a Collection.
  queryables  Get queryable attributes for items in a collection.
  search      Search STAC Items across collections.
  update      Update an existing Item
  validate    Validate a STAC Item.
```

