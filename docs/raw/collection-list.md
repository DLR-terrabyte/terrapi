
# collection list

 List STAC Collections
    
    Collections can be filtered by regular Expressions and written to File 

## Usage

```
Usage: terrapi stac collection list [OPTIONS]
```

## Arguments


## Options

* `filter`:
    * Type: STRING
    * Default: ``
    * Usage: `-f
--filter`

    Filter Collection ID with regex



* `title`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-t
--title`

    Add Title to output



* `description`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-d
--description`

    Add Description to output



* `all`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-a
--all`

    Write whole Collection JSOn to output



* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    Indent Json Printing



* `outfile`:
    * Type: File
    * Default: `stdout`
    * Usage: `-o
--outfile`

    Write Collections to this file instead of stdout



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac collection list [OPTIONS]

  List STAC Collections

  Collections can be filtered by regular Expressions and written to File

Options:
  -f, --filter TEXT       Filter Collection ID with regex
  -t, --title             Add Title to output
  -d, --description       Add Description to output
  -a, --all               Write whole Collection JSOn to output
  -p, --pretty            Indent Json Printing
  -o, --outfile FILENAME  Write Collections to this file instead of stdout
  --help                  Show this message and exit.
```

