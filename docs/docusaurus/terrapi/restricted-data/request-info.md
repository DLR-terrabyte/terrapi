---
id: request-info
title: request-info
description: terrapi command line library documentation - slurm subcommand
---

# restricted-data request-info

Get detailed information about a dataset container.

    This command retrieves and displays detailed information about a dataset container, including:
    - Name
    - DSS ID
    - Associated documents (e.g., EULAs or descriptions)
    - A detailed description of the dataset

    The dataset can be specified by its ID or name.

    Example:
    terrapi restricted-data request-info <dataset-id-or-name>
    

## Usage

```
Usage: terrapi restricted-data request-info [OPTIONS] DATASET
```

## Arguments

* `dataset` (REQUIRED):
    * Type: STRING
    * Default: `None`
    * Usage: `dataset`


## Options

* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi restricted-data request-info [OPTIONS] DATASET

  Get detailed information about a dataset container.

  This command retrieves and displays detailed information about a dataset
  container, including: - Name - DSS ID - Associated documents (e.g., EULAs or
  descriptions) - A detailed description of the dataset

  The dataset can be specified by its ID or name.

  Example: terrapi restricted-data request-info <dataset-id-or-name>

Options:
  --help  Show this message and exit.
```

