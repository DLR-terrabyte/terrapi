
# slurm login

Interactively login via 2FA Browser redirect to obtain refresh Token for the API. 
A Valid Refresh token is needed for all the other sub commands.
It is recommended to call this function first to make sure you have a valid token for the remainder of your job.
This allows the other subcommands to run non-interactively for multiple days.

Use --decode to view the token's contents after login.


## Usage

```
Usage: terrapi slurm login [OPTIONS]
```

## Arguments


## Options

* `force`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-f
--force`

    Force new login, discarding any existing tokens



* `valid`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-v
--valid`

    Will print how long the current Refresh Token is valid.



* `delete`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--delete`

    Delete existing Refresh Token. Will remove the Refresh token if it exists and then exit



* `days`:
    * Type: INT
    * Default: `0`
    * Usage: `-d
--days`

    Min Nr of days the Token needs to be valid. Will refresh Token if it expires earlier



* `hours`:
    * Type: INT
    * Default: `0`
    * Usage: `-h
--hours`

    Min Nr of hours the Token needs valid. Will refresh Token if it expires earlier



* `till`:
    * Type: DateTime
    * Default: `None`
    * Usage: `-t
--till`

    Date the Refresh token needs be valid. Will refresh Token if it expires earlier



* `decode`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--decode`

    Decode and display token contents



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi slurm login [OPTIONS]

  Interactively login via 2FA Browser redirect to obtain refresh Token for the
  API.  A Valid Refresh token is needed for all the other sub commands. It is
  recommended to call this function first to make sure you have a valid token
  for the remainder of your job. This allows the other subcommands to run non-
  interactively for multiple days.

  Use --decode to view the token's contents after login.

Options:
  -f, --force                     Force new login, discarding any existing
                                  tokens
  -v, --valid                     Will print how long the current Refresh
                                  Token is valid.
  --delete                        Delete existing Refresh Token. Will remove
                                  the Refresh token if it exists and then exit
  -d, --days INTEGER              Min Nr of days the Token needs to be valid.
                                  Will refresh Token if it expires earlier
  -h, --hours INTEGER             Min Nr of hours the Token needs valid. Will
                                  refresh Token if it expires earlier
  -t, --till [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]
                                  Date the Refresh token needs be valid. Will
                                  refresh Token if it expires earlier
  --decode                        Decode and display token contents
  --help                          Show this message and exit.
```

