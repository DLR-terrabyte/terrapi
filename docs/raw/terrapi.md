
# terrapi

Terrabyte API Command Line Tool (terrapi)

The Terrabyte client library (terrapi) is a command-line interface (CLI) 
designed to help users interact with protected Terrabyte Application Programming Interfaces (APIs). 

Features:
- User authentication via 2FA website redirection.
- Caching of long-lived refresh tokens in the user's home directory for future API calls.
- Support for specific APIs implemented as subcommands.

Use `terrapi --help` to see available commands and options.


## Usage

```
Usage: terrapi [OPTIONS] COMMAND [ARGS]...
```

## Arguments


## Options

* `debug`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--debug
-d`

    Activate verbose outputs for debugging purposes.



* `version`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--version`

    Show the version and exit.



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi [OPTIONS] COMMAND [ARGS]...

  Terrabyte API Command Line Tool (terrapi)

  The Terrabyte client library (terrapi) is a command-line interface (CLI)
  designed to help users interact with protected Terrabyte Application
  Programming Interfaces (APIs).

  Features: - User authentication via 2FA website redirection. - Caching of
  long-lived refresh tokens in the user's home directory for future API calls.
  - Support for specific APIs implemented as subcommands.

  Use `terrapi --help` to see available commands and options.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  restricted-data  Self Register to restricted Datasets on DSS.
  stac             Command Line Interface for Terrabyte STAC API.
```

