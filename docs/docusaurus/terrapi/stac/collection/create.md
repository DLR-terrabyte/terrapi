---
id: create
title: create
description: terrapi command line library documentation - slurm subcommand
---

# collection create

Create a new STAC Collection 
    
    The Collection json can be specfied either from stdin, from a file or as a parameter. 

    The Stac Server returns updated version of the Collection 

    

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

    Update Collection if it allready exists



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
Usage: terrapi stac collection create [OPTIONS]

  Create a new STAC Collection

  The Collection json can be specfied either from stdin, from a file or as a
  parameter.

  The Stac Server returns updated version of the Collection

Options:
  --id TEXT            ID of the Collection. If specified will overwrite the
                       ID in the Collection JSON
  -j, --json TEXT      Provide collection as JSON String
  -f, --file FILENAME  Read Collection JSON from File. Specify - to read from
                       pipe
  -u, --update         Update Collection if it allready exists
  -q, --quiet          Do not print response
  --help               Show this message and exit.
```

