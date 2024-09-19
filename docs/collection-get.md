
# collection get

Get Metadata for single Collection from its ID

## Usage

```
Usage: terrapi stac collection get [OPTIONS] COLLECTION_ID
```

## Arguments

* `collection_id` (REQUIRED):
    * Type: STRING
    * Default: `None`
    * Usage: `collection_id`


## Options

* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    print pretty readable json



* `outfile`:
    * Type: <click.types.File object at 0x00000289885033E0>
    * Default: `<ConsoleStream name='<stdout>' encoding='utf-16-le'>`
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

  Get Metadata for single Collection from its ID

Options:
  -p, --pretty            print pretty readable json
  -o, --outfile FILENAME  Output file.
  --help                  Show this message and exit.
```

