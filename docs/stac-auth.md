
# stac auth

Print the single use auth token needed to directly interact with the private API

## Usage

```
Usage: terrapi stac auth [OPTIONS]
```

## Arguments


## Options

* `noninteractive`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-n
--noninteractive`

    Fail if no valid Refresh Token stored



* `gdal`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-g
--gdal`

    Add Options needed by gdal



* `curl`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-c
--curl`

    Add Options needed by curl



* `wget`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-w
--wget`

    Add Options needed by wget



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac auth [OPTIONS]

  Print the single use auth token needed to directly interact with the
  private API

Options:
  -n, --noninteractive  Fail if no valid Refresh Token stored
  -g, --gdal            Add Options needed by gdal
  -c, --curl            Add Options needed by curl
  -w, --wget            Add Options needed by wget
  --help                Show this message and exit.
```

