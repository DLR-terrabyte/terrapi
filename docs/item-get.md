
# item get

Get STAC Metadata for a single Item 
It requires the Collection ID and Item ID

## Usage

```
Usage: terrapi stac item get [OPTIONS] COLLECTION_ID ITEM_ID
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

* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    print pretty readable json



* `outfile`:
    * Type: <click.types.File object at 0x0000028988503890>
    * Default: `<ConsoleStream name='<stdout>' encoding='utf-16-le'>`
    * Usage: `-o
--outfile`

    Output file.



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



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item get [OPTIONS] COLLECTION_ID ITEM_ID

  Get STAC Metadata for a single Item  It requires the Collection ID and
  Item ID

Options:
  -p, --pretty            print pretty readable json
  -o, --outfile FILENAME  Output file.
  -a, --assets TEXT       Only Print specified assets, assets are separated by
                          ','

  -h, --href-only         Only Print asset hrefs
  -s, --strip-file        Remove file prefix from asset hrefs
  --help                  Show this message and exit.
```

