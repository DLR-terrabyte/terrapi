
# collection prefix

List all acceptable read/writable prefixes for specific user

The information about the prefixes is extracted from the current refresh token. 
Therefore if a new dss invite was accepted lately it is recommended to force the update of the token via the login function.   


## Usage

```
Usage: terrapi stac collection prefix [OPTIONS]
```

## Arguments


## Options

* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac collection prefix [OPTIONS]

  List all acceptable read/writable prefixes for specific user

  The information about the prefixes is extracted from the current refresh
  token.  Therefore if a new dss invite was accepted lately it is recommended
  to force the update of the token via the login function.

Options:
  --help  Show this message and exit.
```

