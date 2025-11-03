
# item create

Create new Item(s) in specified Collection 

The Item  json can be specfied either from stdin, from a file or as a parameter. 

It can either be the json of a single Item, or to batch create a FeatureCollection with an array of items as features

In case of the list of items make sure they do not exist in collection as update path is not possible in this use case. 

In case of singe Item, the server formated new Item is returned unless quiet flag is passed. 
In case of a FeatureCollections no Items are returned by default. 




## Usage

```
Usage: terrapi stac item create [OPTIONS] COLLECTION_ID
```

## Arguments

* `collection_id` (REQUIRED):
    * Type: STRING
    * Default: `Sentinel.UNSET`
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



* `inputfile`:
    * Type: File
    * Default: `None`
    * Usage: `-f
--file`

    Read Collection JSON from File. Specify - to read from pipe



* `update`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-u
--update`

    Update Item if it allready exists



* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    print pretty readable json



* `quiet`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-q
--quiet`

    Do not print response



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac item create [OPTIONS] COLLECTION_ID

  Create new Item(s) in specified Collection

  The Item  json can be specfied either from stdin, from a file or as a
  parameter.

  It can either be the json of a single Item, or to batch create a
  FeatureCollection with an array of items as features

  In case of the list of items make sure they do not exist in collection as
  update path is not possible in this use case.

  In case of singe Item, the server formated new Item is returned unless quiet
  flag is passed.  In case of a FeatureCollections no Items are returned by
  default.

Options:
  --id TEXT            ID of the Item. If specified will overwrite the ID in
                       the Item JSON
  -j, --json TEXT      Provide collection as JSON String
  -f, --file FILENAME  Read Collection JSON from File. Specify - to read from
                       pipe
  -u, --update         Update Item if it allready exists
  -p, --pretty         print pretty readable json
  -q, --quiet          Do not print response
  --help               Show this message and exit.
```

