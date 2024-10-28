
# terrapi

Terrabyte API CMD Tool: terrapi


     The terrabyte client library terrapi is a small command line interface 
     to support users in interacting with protected terrabyte Application Programming Interfaces (APIs) 
     It encompasses support for user authentication via 2FA website redirection and caches 
     the resulting long lived refresh tokens in the Users Home for use in further API calls.
     
     Specific APIs are implemented as sub commands 

## Usage

```
Usage: terrapi [OPTIONS] COMMAND [ARGS]...
```

## Arguments


## Options

* `debug`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--debug`

    activate verbose outputs



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi [OPTIONS] COMMAND [ARGS]...

  Terrabyte API CMD Tool: terrapi

  The terrabyte client library terrapi is a small command line interface  to
  support users in interacting with protected terrabyte Application
  Programming Interfaces (APIs)  It encompasses support for user
  authentication via 2FA website redirection and caches  the resulting long
  lived refresh tokens in the Users Home for use in further API calls.

  Specific APIs are implemented as sub commands

Options:
  --help  Show this message and exit.

Commands:
  stac  Command Line for terrabyte private STAC API The private Stac Api...
```

