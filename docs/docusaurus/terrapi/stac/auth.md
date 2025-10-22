---
id: auth
title: auth
description: terrapi command line library documentation - stac subcommand
---

# stac auth

Print the single use auth token needed to directly interact with authenticated terrabyte APIs

Optionally will add the parameters needed for utilities like curl or wget.
The returned Token is only valid for a few minutes.
Use --decode to view the token's contents.

For use in subshell commands, use the --subshell flag:

    
Bash/Zsh:
    curl -H "$(terrapi auth -c)"  https://stac.terrabyte.lrz.de/private/api/collections
    wget --header="$(terrapi auth -w)"  https://stac.terrabyte.lrz.de/private/api/collections

    echo Curl example curl $(terrapi auth -c -e)  https://stac.terrabyte.lrz.de/private/api/collections


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



* `decode`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--decode`

    Decode and display token contents



* `echo`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-e
--echo`

    Format output for curl or wget to use on echo c&p



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac auth [OPTIONS]

  Print the single use auth token needed to directly interact with
  authenticated terrabyte APIs

  Optionally will add the parameters needed for utilities like curl or wget.
  The returned Token is only valid for a few minutes. Use --decode to view the
  token's contents.

  For use in subshell commands, use the --subshell flag:

       Bash/Zsh:     curl -H "$(terrapi auth -c)"
      https://stac.terrabyte.lrz.de/private/api/collections     wget
      --header="$(terrapi auth -w)"
      https://stac.terrabyte.lrz.de/private/api/collections

      echo Curl example curl $(terrapi auth -c -e)
      https://stac.terrabyte.lrz.de/private/api/collections

Options:
  -n, --noninteractive  Fail if no valid Refresh Token stored
  -g, --gdal            Add Paramter needed by gdal
  -c, --curl            Add Paramter needed by curl
  -w, --wget            Add Paramter needed by wget
  --decode              Decode and display token contents
  -e, --echo            Format output for curl or wget to use on echo c&p
  --help                Show this message and exit.
```

