# Terrabyte STAC Best Practice Guide

This guide outlines the standards and best practices for STAC metadata in the Terrabyte infrastructure. Following these practices ensures your data is discoverable, interoperable, and fully compatible with modern STAC tools like Open Data Cube (ODC).

## 1. Automatic Metadata Enrichment (Mandatory)

The Terrabyte API automatically injects several required fields into your STAC Items and Collections upon creation or update.

- **Contacts Extension ([v0.1.1](https://stac-extensions.github.io/contacts/v0.1.1/schema.json))**:
  - Automatically derived from 2FA Token.
  - `name`: User's preferred username.
  - `emails`: User's email address.
  - `roles`: Defaults to `["contact"]`.
- **RFC 3339 Timestamps**:
  - `created`: Injected if missing.
  - `updated`: Automatically updated on every modification.

## 2. Hard Validation Rules (Errors)

Metadata that fails these checks will be rejected unless the `--force` flag is used.

- **ID Validation**: IDs must be alphanumeric and can include `_`, `-`, or `.`.
- **STAC Version**: Must follow the STAC specification (e.g., `1.0.0`).
- **Asset URL Scheme**: All asset `hrefs` must use `http`, `https`, or `file` schemes.
- **Asset URL Prefix**: Absolute `file:///` URLs must match the collection's prefix (or the user's allowed prefixes) to prevent cross-workspace references.

## 3. ODC-STAC Best Practices (Warnings)

While not strictly required, including these fields significantly improves the user experience when using tools like `odc-stac`.

### Raster Extension ([raster](https://github.com/stac-extensions/raster))
- **`data_type`**: Describe the pixel type (e.g., `uint16`, `float32`). Used to determine output pixel type.
- **`nodata`**: Specify the "no data" value. Essential for combining multiple items into a single raster plane.

### Projection Extension ([proj](https://github.com/stac-extensions/projection))
- **`proj:shape`**: Include the image size (height, width) per asset.
- **`proj:transform`**: Include the geo-registration (6-element affine transform).
- **`proj:epsg`**: Include the native Coordinate Reference System (CRS) as an EPSG code.
- **`proj:wkt2` / `proj:projjson`**: Use for CRS without an EPSG code.

### Electro Optical Extension ([eo](https://github.com/stac-extensions/eo))
- **`eo:bands.common_name`**: Provide friendly aliases for bands (e.g., use `red` instead of `B04`).

## 4. Collection Consistency

- **Uniformity**: Items within the same collection should have the same number and names of bands.
- **Consistency**: Bands should use the same `data_type` across the entire collection.
- **Projection**: Assets within a single Item are assumed to share a common native projection.
