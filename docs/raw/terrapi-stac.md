
# terrapi stac

Command Line Interface for Terrabyte STAC API.

    The STAC API allows users to interact with geospatial data collections and items. 

    Features:
    - Create, update, and delete private STAC collections and items.
    - Query public or private STAC APIs for metadata and assets.
    - Filter collections and items by spatial, temporal, and asset properties.

    Use the `--public` flag to switch to the public API for read-only access to curated datasets.

    Examples:
    - List all collections: `terrapi stac collection list`
    - Get metadata for a collection: `terrapi stac collection get <collection_id>`
    - Create a new item: `terrapi stac item create <collection_id> --file item.json`
    

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

    Switch to public API for read-only access.



* `private_url`:
    * Type: STRING
    * Default: `None`
    * Usage: `--privateURL`

    Override private STAC API URL. (Expert option)



* `public_url`:
    * Type: STRING
    * Default: `None`
    * Usage: `--publicURL`

    Override public STAC API URL. (Expert option)



* `client_id`:
    * Type: STRING
    * Default: `None`
    * Usage: `--clientID`

    Override client ID. (Expert option)



* `help`:
    * Type: BOOL
    * Default: `False`
    * Usage: `--help`

    Show this message and exit.



## CLI Help

```
Usage: terrapi stac [OPTIONS] COMMAND [ARGS]...

  Command Line Interface for Terrabyte STAC API.

  The STAC API allows users to interact with geospatial data collections and
  items.

  Features: - Create, update, and delete private STAC collections and items. -
  Query public or private STAC APIs for metadata and assets. - Filter
  collections and items by spatial, temporal, and asset properties.

  Use the `--public` flag to switch to the public API for read-only access to
  curated datasets.

  Examples: - List all collections: `terrapi stac collection list` - Get
  metadata for a collection: `terrapi stac collection get <collection_id>` -
  Create a new item: `terrapi stac item create <collection_id> --file
  item.json`

Options:
  -p, --public       Switch to public API for read-only access.
  --privateURL TEXT  Override private STAC API URL. (Expert option)
  --publicURL TEXT   Override public STAC API URL. (Expert option)
  --help             Show this message and exit.

Commands:
  auth        Print the single use auth token needed to directly interact...
  collection  Manage STAC Collections.
  item        Manage STAC Items.
  login       Interactively login via 2FA Browser redirect to obtain...
```

