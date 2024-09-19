
# collection create

Create a Collection from either String or File

## Usage

```
Usage: terrapi stac collection create [OPTIONS]
```

## Arguments


## Options

* `id`:
    * Type: STRING
    * Default: `None`
    * Usage: `--id`

    ID of the Collection. If specified will overwrite the ID in the Collection JSON



* `json_str`:
    * Type: STRING
    * Default: `None`
    * Usage: `-j
--json`

    Provide collection as JSON String



* `inputfile`:
    * Type: <click.types.File object at 0x0000028988502D80>
    * Default: `None`
    * Usage: `-f
--file`

    Read Collection JSON from File. Specify - to read from pipe



* `update`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-u
--update`

    Update Collection if it allready exists



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac collection create [OPTIONS]

  Create a Collection from either String or File

Options:
  --id TEXT            ID of the Collection. If specified will overwrite the
                       ID in the Collection JSON

  -j, --json TEXT      Provide collection as JSON String
  -f, --file FILENAME  Read Collection JSON from File. Specify - to read from
                       pipe

  -u, --update         Update Collection if it allready exists
  --help               Show this message and exit.
```

