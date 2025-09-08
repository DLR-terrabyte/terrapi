
# restricted-data auth

Print the single use auth token needed to directly interact with private terrapbyte APIs

Optionally will add the parameters needed for utilities like curl or wget.
The returned Token is only valid for a few minutes. 



## Usage

```
Usage: terrapi restricted-data auth [OPTIONS]
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

    Add Paramter needed by gdal



* `curl`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-c
--curl`

    Add Paramter needed by curl



* `wget`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-w
--wget`

    Add Paramter needed by wget



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi restricted-data auth [OPTIONS]

  Print the single use auth token needed to directly interact with private
  terrapbyte APIs

  Optionally will add the parameters needed for utilities like curl or wget.
  The returned Token is only valid for a few minutes.

Options:
  -n, --noninteractive  Fail if no valid Refresh Token stored
  -g, --gdal            Add Paramter needed by gdal
  -c, --curl            Add Paramter needed by curl
  -w, --wget            Add Paramter needed by wget
  --help                Show this message and exit.
```

