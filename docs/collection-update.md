
# collection update

Update an existing Collection from either String or File

## Usage

```
Usage: terrapi stac collection update [OPTIONS]
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
    * Type: <click.types.File object at 0x0000028988502FF0>
    * Default: `None`
    * Usage: `-f
--file`

    Read Collection JSON from File. Specify - to read from pipe



* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    print pretty readable json



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac collection update [OPTIONS]

  Update an existing Collection from either String or File

Options:
  --id TEXT            ID of the Collection. If specified will overwrite the
                       ID in the Collection JSON

  -j, --json TEXT      Provide collection as JSON String
  -f, --file FILENAME  Read Collection JSON from File. Specify - to read from
                       pipe

  -p, --pretty         print pretty readable json
  --help               Show this message and exit.
```

