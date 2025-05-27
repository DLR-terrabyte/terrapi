
# terrapi restricted-data

 Self Register to restricted Datasets on DSS. 
        This tool allows you to get an overview of currently available restricted datasets, your current access status and their usage restrictions/requirements. 
        Request access to datasets by accepting their specific EULAs 
    

## Usage

```
Usage: terrapi restricted-data [OPTIONS] COMMAND [ARGS]...
```

## Arguments


## Options

* `local`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-l`

    Development Option to talk to backend locally (port 8000) 



* `testing`:
    * Type: BOOL
    * Default: `False`
    * Usage: `-t`

    Development Option to talk to testing backend 



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi restricted-data [OPTIONS] COMMAND [ARGS]...

  Self Register to restricted Datasets on DSS.  This tool allows you to get an
  overview of currently available restricted datasets, your current access
  status and their usage restrictions/requirements.  Request access to
  datasets by accepting their specific EULAs

Options:
  -l      Development Option to talk to backend locally (port 8000)
  -t      Development Option to talk to testing backend
  --help  Show this message and exit.

Commands:
  auth            Print the single use auth token needed to directly...
  list-available  List all restricted datasets available on Terrabyte DSS.
  login           Interactively login via 2FA Browser redirect to obtain...
  request-access  Request access to a specific dataset on Terrabyte DSS.
  request-info    Get detailed information about a dataset container.
```

