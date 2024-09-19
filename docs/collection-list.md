
# collection list

List Collections

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

    Write whole JSOn to output



* `pretty`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--pretty`

    Indent Json Printing



* `outfile`:
    * Type: <click.types.File object at 0x0000028988502300>
    * Default: `<ConsoleStream name='<stdout>' encoding='utf-16-le'>`
    * Usage: `-o
--outfile`

    Write Output to this file



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac collection list [OPTIONS]

  List Collections

Options:
  -f, --filter TEXT       Filter Collection ID with regex
  -t, --title             Add Title to output
  -d, --description       Add Description to output
  -a, --all               Write whole JSOn to output
  -p, --pretty            Indent Json Printing
  -o, --outfile FILENAME  Write Output to this file
  --help                  Show this message and exit.
```

