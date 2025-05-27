
# restricted-data request-access

Request access to a specific dataset on Terrabyte DSS.

    This command allows you to interactively request access to a dataset by accepting its End User License Agreement (EULA).
    The dataset can be specified by its ID or name. Some datasets may be restricted to specific user groups (e.g., DLR employees, specific Insitutes or Departments).

    Steps:
    - Displays the dataset's details, including its name, ID, description, and associated documents.
    - Prompts you to confirm that you have read and accepted the EULA.
    - Sends a request to the backend to grant access to the dataset.

    Example:
    terrapi restricted-data request-access <dataset-id-or-name>
    

## Usage

```
Usage: terrapi restricted-data request-access [OPTIONS] DATASET
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
Usage: terrapi restricted-data request-access [OPTIONS] DATASET

  Request access to a specific dataset on Terrabyte DSS.

  This command allows you to interactively request access to a dataset by
  accepting its End User License Agreement (EULA). The dataset can be
  specified by its ID or name. Some datasets may be restricted to specific
  user groups (e.g., DLR employees, specific Insitutes or Departments).

  Steps: - Displays the dataset's details, including its name, ID,
  description, and associated documents. - Prompts you to confirm that you
  have read and accepted the EULA. - Sends a request to the backend to grant
  access to the dataset.

  Example: terrapi restricted-data request-access <dataset-id-or-name>

Options:
  --help  Show this message and exit.
```

