
# item delete

 Delete an Item from Collection
    
    
    This will permanently delete the specified Item from the STAC Catalogue
    

## Usage

```
Usage: terrapi stac item delete [OPTIONS] COLLECTION_ID ITEM_ID
```

## Arguments

* `collection_id` (REQUIRED):
    * Type: STRING
    * Default: `None`
    * Usage: `collection_id`


* `item_id` (REQUIRED):
    * Type: STRING
    * Default: `None`
    * Usage: `item_id`


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
Usage: terrapi stac item delete [OPTIONS] COLLECTION_ID ITEM_ID

  Delete an Item from Collection

  This will permanently delete the specified Item from the STAC Catalogue

Options:
  --yes   Confirm deletion.
  --help  Show this message and exit.
```

