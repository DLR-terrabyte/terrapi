---
id: stac
title: stac
description: terrapi command line library documentation - slurm subcommand
---

# terrapi stac

Command Line for terrabyte private STAC API
    The private Stac Api allows you to create/update your own private or shared (between all users of a dss container) STAC Collections and Items
    To mark a collection as private prepend the name of the collection with your LRZ username, e.g., something like "di99abc.Sentinel2Classification"
    To mark a collection as shared prepend its name with DSS Container ID  like "pn56su-dss-0020" 
    All write/readable prefixes can be obtained from the sub command prefix.
    The public flag allows the read-only usage of terrapi for the currated public STAC API 
    

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

    overwrite clientID.  Warning expert OPTION!



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac [OPTIONS] COMMAND [ARGS]...

  Command Line for terrabyte private STAC API The private Stac Api allows you
  to create/update your own private or shared (between all users of a dss
  container) STAC Collections and Items To mark a collection as private
  prepend the name of the collection with your LRZ username, e.g., something
  like "di99abc.Sentinel2Classification" To mark a collection as shared
  prepend its name with DSS Container ID  like "pn56su-dss-0020"  All
  write/readable prefixes can be obtained from the sub command prefix. The
  public flag allows the read-only usage of terrapi for the currated public
  STAC API

Options:
  -p, --public       Switch to public API
  --privateURL TEXT  overwrite private Stac URL.  Warning expert OPTION!
  --publicURL TEXT   overwrite public Stac URL.  Warning expert OPTION!
  --help             Show this message and exit.

Commands:
  auth        Print the single use auth token needed to directly interact...
  collection  Interact with STAC Collection(s)
  item        Interact with Stac Item(s)
  login       Interactively login via 2FA Browser redirect to obtain...
```

