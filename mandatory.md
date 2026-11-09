# Mandatory STAC Fields for Private API

To ensure consistency and provide contact information for all geospatial data in the private STAC catalog, several fields are automatically managed by the CLI when creating or updating items and collections.

## Automatically Added Fields

When you use the `terrapi stac` commands to create or update STAC objects, the following fields are automatically populated using information from your authentication token (JWT) and the current system time.

### 1. Contacts Extension
The project adheres to the [STAC Contacts Extension (v1.0.0)](https://github.com/stac-extensions/contacts).
- **Field**: `stac_extensions`
- **Value**: Adds `https://stac-extensions.github.io/contacts/v1.0.0/schema.json` to the list of extensions.

### 2. Contact Information
Your user information is automatically added as a contact.
- **Field**: `contacts`
- **Structure**:
  - `name`: Your `preferred_username` from the auth token.
  - `emails`: A list containing your `email` address from the auth token.
  - `roles`: Defaults to `["contact"]`.

### 3. Timestamps
Standard metadata for tracking the creation and modification time.
- **Field**: `created` (RFC 3339 UTC timestamp)
- **Field**: `updated` (RFC 3339 UTC timestamp)

---

## Examples

### STAC Item (Feature)
For single items, these fields are added within the `properties` dictionary.

```json
{
  "type": "Feature",
  "id": "my-item-id",
  "stac_extensions": [
    "https://stac-extensions.github.io/contacts/v1.0.0/schema.json"
  ],
  "properties": {
    "contacts": [
      {
        "roles": ["contact"],
        "name": "jdoe",
        "emails": ["j.doe@example.com"]
      }
    ],
    "created": "2026-03-25T13:19:49Z",
    "updated": "2026-03-25T13:19:49Z"
  },
  ...
}
```

### STAC Collection
For collections, these fields are added at the **top level**.

```json
{
  "type": "Collection",
  "id": "my-collection-id",
  "stac_extensions": [
    "https://stac-extensions.github.io/contacts/v1.0.0/schema.json"
  ],
  "contacts": [
    {
      "roles": ["contact"],
      "name": "jdoe",
      "emails": ["j.doe@example.com"]
    }
  ],
  "created": "2026-03-25T13:19:49Z",
  "updated": "2026-03-25T13:19:49Z",
  ...
}
```

## Note on 'created' field
By default, the `created` field is only set if it does not already exist. The `updated` field is always refreshed to the current time on every update operation.
