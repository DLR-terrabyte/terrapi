
# terrapi stac

Command Line for terrabyte private STAC API

## Usage

```
Usage: terrapi stac [OPTIONS] COMMAND [ARGS]...
```

## Arguments


## Options

* `public`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-p
--public`

    Switch to public API



* `private_url`:
    * Type: STRING
    * Default: `None`
    * Usage: `--privateURL`

    overwrite private Stac URL.  Warning expert OPTION! 



* `public_url`:
    * Type: STRING
    * Default: `None`
    * Usage: `--publicURL`

    overwrite public Stac URL.  Warning expert OPTION! 



* `client_id`:
    * Type: STRING
    * Default: `None`
    * Usage: `--clientID`

    overwrite clientID



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac [OPTIONS] COMMAND [ARGS]...

  Command Line for terrabyte private STAC API

Options:
  -p, --public       Switch to public API
  --privateURL TEXT  overwrite private Stac URL.  Warning expert OPTION!
  --publicURL TEXT   overwrite public Stac URL.  Warning expert OPTION!
  --help             Show this message and exit.

Commands:
  auth        Print the single use auth token needed to directly interact...
  collection  Interact with STAC Collection(s)
  item        Interact with Stac Item(s)
  login       Interactively login via 2FA to obtain refresh Token for the...
```

