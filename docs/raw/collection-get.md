
# collection get

 Get STAC Metadata for a single Collection 
    
    It requires the Collection ID as an Argument
    

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
    * Type: File
    * Default: `stdout`
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

  Get STAC Metadata for a single Collection

  It requires the Collection ID as an Argument

Options:
  -p, --pretty            print pretty readable json
  -o, --outfile FILENAME  Output file.
  --help                  Show this message and exit.
```

