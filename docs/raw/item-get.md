
# item get

Retrieve metadata for a single STAC item.

    This command fetches metadata for a specific item in a collection. Use the `--href-only` option to print only asset hrefs.

    Examples:
    - Get item metadata: `terrapi stac item get <collection_id> <item_id>`
    - Get asset hrefs: `terrapi stac item get <collection_id> <item_id> --href-only`
    

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

    Pretty-print JSON output.



* `outfile`:
    * Type: File
    * Default: `<_io.TextIOWrapper name='<stdout>' encoding='utf-8'>`
    * Usage: `-o
--outfile`

    Write output to a file instead of stdout.



* `assetfilter`:
    * Type: STRING
    * Default: `None`
    * Usage: `-a
--assets`

    Only print specified assets, multiple assets are separated by ','.



* `href_only`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-r
--href-only`

    Only print asset hrefs.



* `strip_file`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-s
--strip-file`

    Remove file prefix from asset hrefs.



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item get [OPTIONS] COLLECTION_ID ITEM_ID

  Retrieve metadata for a single STAC item.

  This command fetches metadata for a specific item in a collection. Use the
  `--href-only` option to print only asset hrefs.

  Examples: - Get item metadata: `terrapi stac item get <collection_id>
  <item_id>` - Get asset hrefs: `terrapi stac item get <collection_id>
  <item_id> --href-only`

Options:
  -p, --pretty            Pretty-print JSON output.
  -o, --outfile FILENAME  Write output to a file instead of stdout.
  -a, --assets TEXT       Only print specified assets, multiple assets are
                          separated by ','.
  -r, --href-only         Only print asset hrefs.
  -s, --strip-file        Remove file prefix from asset hrefs.
  --help                  Show this message and exit.
```

