
# item update

Update an existing Item 

The Item  json can be specfied either from stdin, from a file or as a parameter.


## Usage

```
Usage: terrapi stac item update [OPTIONS] COLLECTION_ID
```

## Arguments

* `collection_id` (REQUIRED):
    * Type: STRING
    * Default: `None`
    * Usage: `collection_id`


## Options

* `item_id`:
    * Type: STRING
    * Default: `None`
    * Usage: `--id`

    ID of the Item. If specified will overwrite the ID in the Item JSON



* `json_str`:
    * Type: STRING
    * Default: `None`
    * Usage: `-j
--json`

    Provide collection as JSON String



* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    print pretty readable json



* `inputfile`:
    * Type: File
    * Default: `None`
    * Usage: `-f
--file`

    Read Collection JSON from File. Specify - to read from pipe



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item update [OPTIONS] COLLECTION_ID

  Update an existing Item

  The Item  json can be specfied either from stdin, from a file or as a
  parameter.

Options:
  --id TEXT            ID of the Item. If specified will overwrite the ID in
                       the Item JSON
  -j, --json TEXT      Provide collection as JSON String
  -p, --pretty         print pretty readable json
  -f, --file FILENAME  Read Collection JSON from File. Specify - to read from
                       pipe
  --help               Show this message and exit.
```

