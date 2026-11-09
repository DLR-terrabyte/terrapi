import pytest
from terrapi.private.stac import (
    validate_item,
    validate_collection,
    update_mandatory_fields,
    validate_id,
    validate_extensions,
    get_valid_prefixes,
    parse_extension_info,
    parse_version_tuple,
    is_version_older,
    check_extension_versions,
    LATEST_EXTENSIONS,
    REQUIRED_EXTENSIONS,
    RECOMMENDED_EXTENSIONS,
)

def test_validate_item_basic():
    """Test basic STAC Item validation."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "test-item",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {
            "datetime": "2023-01-01T00:00:00Z",
            "contacts": [{"roles": ["contact"]}]
        },
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v0.1.1/schema.json"],
        "assets": {
            "data": {"href": "https://example.com/data.tif"}
        }
    }
    # Should be valid
    assert validate_item(item) is True

def test_validate_item_missing_fields():
    """Test validation fails when required fields are missing."""
    item = {"type": "Feature", "id": "test"}
    assert validate_item(item) is False

def test_validate_item_invalid_asset_scheme():
    """Test validation fails with invalid asset URL scheme."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "test-item",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00-00:00", "contacts": [{"roles": ["contact"]}]},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v0.1.1/schema.json"],
        "assets": {
            "data": {"href": "s3://bucket/data.tif"} # Invalid scheme
        }
    }
    assert validate_item(item) is False

def test_validate_item_prefix_check():
    """Test validation of file:/// URLs against collection prefix."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "test-item",
        "collection": "myusername.collection",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z", "contacts": [{"roles": ["contact"]}]},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v0.1.1/schema.json"],
        "assets": {
            "data": {"href": "file:///path/to/myusername/data.tif"}
        }
    }
    # Should be valid because 'myusername' is in the href
    assert validate_item(item) is True

    # Invalid prefix
    item["assets"]["data"]["href"] = "file:///path/to/otheruser/data.tif"
    assert validate_item(item) is False

def test_best_practice_warnings(capsys):
    """Test that best practice warnings are printed but don't fail validation."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "test-item",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {
            "datetime": "2023-01-01T00:00:00Z",
            "contacts": [{"roles": ["contact"]}]
        },
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v0.1.1/schema.json"],
        "assets": {
            "data": {"href": "https://example.com/data.tif"}
        }
    }
    # No raster/proj extensions -> should trigger warnings but pass
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "STAC Item Best Practice Warnings" in captured.err
    assert "Missing recommended STAC extension" in captured.err

def test_update_mandatory_fields():
    """Test that mandatory fields are correctly injected into STAC Item properties."""
    item = {
        "type": "Feature",
        "properties": {}
    }
    token = {
        "preferred_username": "testuser",
        "email": "test@example.com"
    }
    # Mocking JWT decode internally happens in update_mandatory_fields if token is passed as dict
    updated = update_mandatory_fields(item, decoded_token=token)
    
    assert "contacts" in updated["properties"]
    assert updated["properties"]["contacts"][0]["name"] == "testuser"
    assert "created" in updated["properties"]
    assert "updated" in updated["properties"]
    assert "https://stac-extensions.github.io/contacts/v1.0.0/schema.json" in updated["stac_extensions"]

def test_validate_collection():
    """Test basic STAC Collection validation."""
    collection = {
        "stac_version": "1.0.0",
        "type": "Collection",
        "id": "test-collection",
        "description": "test",
        "license": "MIT",
        "extent": {
            "spatial": {"bbox": [[0,0,0,0]]},
            "temporal": {"interval": [[None, None]]}
        },
        "links": []
    }
    # Fails because contacts extension is now required by Terrabyte rules
    assert validate_collection(collection) is False
    
    # Add contacts
    collection["stac_extensions"] = ["https://stac-extensions.github.io/contacts/v1.0.0/schema.json"]
    assert validate_collection(collection) is True

def test_older_extension_version_warning(capsys):
    """Test that a warning is issued if an extension version is older than the recommended version."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "test-item-older-ext",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {
            "datetime": "2023-01-01T00:00:00Z",
            "contacts": [{"roles": ["contact"]}]
        },
        "stac_extensions": [
            "https://stac-extensions.github.io/contacts/v0.1.1/schema.json",
            "https://stac-extensions.github.io/raster/v1.1.0/schema.json"
        ],
        "assets": {
            "data": {"href": "https://example.com/data.tif"}
        }
    }
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "STAC Item Best Practice Warnings" in captured.err
    assert "STAC extension 'contacts' version '0.1.1' is older than recommended version '1.0.0'" in captured.err
    assert "STAC extension 'raster' version '1.1.0' is older than recommended version '2.0.0'" in captured.err

# --- Additional Comprehensive Test Cases ---

def test_extension_helpers():
    """Test helper functions for STAC extension version parsing and comparison."""
    # parse_extension_info
    assert parse_extension_info(None) == (None, None)
    assert parse_extension_info(123) == (None, None)
    assert parse_extension_info("https://example.com/schema.json") == (None, None)
    assert parse_extension_info("https://stac-extensions.github.io/contacts/v1.0.0/schema.json") == ("contacts", "1.0.0")
    assert parse_extension_info("https://stac-extensions.github.io/projection/2.0.0/schema.json") == ("projection", "2.0.0")
    
    # parse_version_tuple
    assert parse_version_tuple("1.0.0") == (1, 0, 0)
    assert parse_version_tuple("v2.1") == (2, 1)
    assert parse_version_tuple("invalid") == (0,)
    
    # is_version_older
    assert is_version_older("0.1.1", "1.0.0") is True
    assert is_version_older("1.0.0", "1.0.0") is False
    assert is_version_older("2.0.0", "1.0.0") is False
    assert is_version_older("1.1.0", "2.0.0") is True

def test_validate_id():
    """Test STAC ID validation according to pgstac / fastAPI regex."""
    assert validate_id("valid_id-123.test") is True
    assert validate_id("A" * 255) is True
    
    assert validate_id("") is False
    assert validate_id("invalid id with spaces") is False
    assert validate_id("id/with/slashes") is False
    assert validate_id("id:with:colons") is False
    assert validate_id("id@special!") is False
    assert validate_id("A" * 256) is False

def test_validate_item_and_collection_invalid_id():
    """Test that items and collections with invalid IDs fail validation."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "invalid id spaces",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v1.0.0/schema.json"],
        "assets": {"data": {"href": "https://example.com/data.tif"}}
    }
    assert validate_item(item) is False

    collection = {
        "stac_version": "1.0.0",
        "type": "Collection",
        "id": "invalid/id/slash",
        "description": "test",
        "license": "MIT",
        "extent": {"spatial": {"bbox": [[0,0,0,0]]}, "temporal": {"interval": [[None, None]]}},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v1.0.0/schema.json"]
    }
    assert validate_collection(collection) is False

def test_validate_item_geometry_bbox_assets():
    """Test validation errors for malformed bbox, geometry, properties, and assets."""
    base_item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "valid-id",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v1.0.0/schema.json"],
        "assets": {"data": {"href": "https://example.com/data.tif"}}
    }
    
    # Invalid bbox: not 4 elements or not a list
    assert validate_item(dict(base_item, bbox=[0, 0, 0])) is False
    assert validate_item(dict(base_item, bbox="not-a-list")) is False
    
    # Invalid geometry: not a dict
    assert validate_item(dict(base_item, geometry="Point")) is False
    assert validate_item(dict(base_item, geometry=None)) is False
    
    # Invalid properties: not a dict
    assert validate_item(dict(base_item, properties="not-a-dict")) is False
    
    # Invalid assets: empty dictionary or None
    assert validate_item(dict(base_item, assets={})) is False
    assert validate_item(dict(base_item, assets=None)) is False
    
    # Asset missing href
    assert validate_item(dict(base_item, assets={"data": {}})) is False

def test_validate_feature_collection():
    """Test validation of FeatureCollection objects."""
    single_valid_item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "item-1",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v1.0.0/schema.json"],
        "assets": {"data": {"href": "https://example.com/data.tif"}}
    }
    
    # Valid FeatureCollection
    fc = {
        "type": "FeatureCollection",
        "features": [single_valid_item, dict(single_valid_item, id="item-2")]
    }
    assert validate_item(fc) is True
    
    # Missing features list
    assert validate_item({"type": "FeatureCollection"}) is False
    assert validate_item({"type": "FeatureCollection", "features": "not-a-list"}) is False
    
    # One invalid feature in collection
    fc_with_invalid = {
        "type": "FeatureCollection",
        "features": [single_valid_item, {"type": "Feature", "id": "bad-item"}]
    }
    assert validate_item(fc_with_invalid) is False

def test_update_mandatory_fields_feature_collection():
    """Test injecting mandatory fields into each item of a FeatureCollection."""
    fc = {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature", "id": "fc-item-1", "properties": {}},
            {"type": "Feature", "id": "fc-item-2", "properties": {}}
        ]
    }
    token = {"preferred_username": "fcuser", "email": "fcuser@example.com"}
    updated = update_mandatory_fields(fc, decoded_token=token)
    
    assert len(updated["features"]) == 2
    for feat in updated["features"]:
        assert feat["properties"]["contacts"][0]["name"] == "fcuser"
        assert feat["properties"]["contacts"][0]["emails"] == ["fcuser@example.com"]
        assert "created" in feat["properties"]
        assert "updated" in feat["properties"]
        assert "https://stac-extensions.github.io/contacts/v1.0.0/schema.json" in feat["stac_extensions"]

def test_update_mandatory_fields_collection():
    """Test that mandatory fields are added at the top level for Collections."""
    collection = {
        "type": "Collection",
        "id": "my-col"
    }
    token = {"preferred_username": "coluser", "email": "coluser@example.com"}
    updated = update_mandatory_fields(collection, decoded_token=token)
    
    # Must be at root level, NOT under properties
    assert "properties" not in updated
    assert "contacts" in updated
    assert updated["contacts"][0]["name"] == "coluser"
    assert updated["contacts"][0]["emails"] == ["coluser@example.com"]
    assert "created" in updated
    assert "updated" in updated
    assert "https://stac-extensions.github.io/contacts/v1.0.0/schema.json" in updated["stac_extensions"]

def test_update_mandatory_fields_in_place_extension_upgrade():
    """Test that an older contacts extension is replaced in-place without duplicates."""
    item = {
        "type": "Feature",
        "stac_extensions": [
            "https://stac-extensions.github.io/contacts/v0.1.1/schema.json",
            "https://stac-extensions.github.io/raster/v2.0.0/schema.json"
        ],
        "properties": {}
    }
    token = {"preferred_username": "testuser"}
    updated = update_mandatory_fields(item, decoded_token=token)
    
    assert len(updated["stac_extensions"]) == 2
    assert updated["stac_extensions"][0] == "https://stac-extensions.github.io/contacts/v1.0.0/schema.json"
    assert updated["stac_extensions"][1] == "https://stac-extensions.github.io/raster/v2.0.0/schema.json"

def test_update_mandatory_fields_created_timestamp_behavior():
    """Test preservation vs overwrite of 'created' timestamp."""
    original_created = "2020-01-01T00:00:00Z"
    item = {
        "type": "Feature",
        "properties": {"created": original_created}
    }
    token = {"preferred_username": "testuser"}
    
    # Default: preserve existing created
    updated = update_mandatory_fields(item.copy(), decoded_token=token, allways_set_created=False)
    assert updated["properties"]["created"] == original_created
    assert updated["properties"]["updated"] != original_created
    
    # allways_set_created=True: overwrite created
    overwritten = update_mandatory_fields(item.copy(), decoded_token=token, allways_set_created=True)
    assert overwritten["properties"]["created"] != original_created

def test_skip_asset_validation():
    """Test that skip_asset_validation bypasses scheme and prefix checks."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "test-skip",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v1.0.0/schema.json"],
        "assets": {
            "invalid_scheme": {"href": "s3://mybucket/test.tif"}
        }
    }
    assert validate_item(item, skip_asset_validation=False) is False
    assert validate_item(item, skip_asset_validation=True) is True

def test_odc_stac_raster_warnings(capsys):
    """Test best practice warnings for the raster extension."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "raster-item",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": [
            "https://stac-extensions.github.io/contacts/v1.0.0/schema.json",
            "https://stac-extensions.github.io/raster/v2.0.0/schema.json"
        ],
        "assets": {
            "band_missing_fields": {
                "href": "https://example.com/data.tif",
                "raster:bands": [{}] # missing data_type and nodata
            }
        }
    }
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "missing 'data_type'" in captured.err
    assert "missing 'nodata'" in captured.err

    # Missing raster:bands entirely
    item["assets"]["band_missing_fields"] = {"href": "https://example.com/data.tif"}
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "is missing 'raster:bands' while using raster extension" in captured.err

def test_odc_stac_projection_warnings(capsys):
    """Test best practice warnings for projection extension."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "proj-item",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": [
            "https://stac-extensions.github.io/contacts/v1.0.0/schema.json",
            "https://stac-extensions.github.io/projection/v2.0.0/schema.json"
        ],
        "assets": {
            "data": {"href": "https://example.com/data.tif"}
        }
    }
    # Missing proj fields in asset and properties
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "Missing 'proj:epsg'" in captured.err
    assert "Missing 'proj:shape'" in captured.err
    assert "Missing 'proj:transform'" in captured.err

    # Providing projection fields in item properties satisfies best practice
    item["properties"]["proj:epsg"] = 4326
    item["properties"]["proj:shape"] = [100, 100]
    item["properties"]["proj:transform"] = [1, 0, 0, 0, 1, 0]
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "Missing 'proj:" not in captured.err

def test_odc_stac_eo_warnings(capsys):
    """Test best practice warnings for EO extension."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "eo-item",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": [
            "https://stac-extensions.github.io/contacts/v1.0.0/schema.json",
            "https://stac-extensions.github.io/eo/v2.0.0/schema.json"
        ],
        "assets": {
            "data": {
                "href": "https://example.com/data.tif",
                "eo:bands": [{}] # missing common_name
            }
        }
    }
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "is missing 'common_name'" in captured.err

    # Asset missing eo:bands entirely
    item["assets"]["data"] = {"href": "https://example.com/data.tif"}
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "is missing 'eo:bands' while using eo extension" in captured.err

def test_fully_compliant_odc_stac_item(capsys):
    """Test that a fully compliant STAC item emits zero warnings."""
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "compliant-item",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {
            "datetime": "2023-01-01T00:00:00Z",
            "contacts": [{"roles": ["contact"]}]
        },
        "stac_extensions": [
            "https://stac-extensions.github.io/contacts/v1.0.0/schema.json",
            "https://stac-extensions.github.io/raster/v2.0.0/schema.json",
            "https://stac-extensions.github.io/projection/v2.0.0/schema.json",
            "https://stac-extensions.github.io/eo/v2.0.0/schema.json"
        ],
        "assets": {
            "data": {
                "href": "https://example.com/data.tif",
                "raster:bands": [{"data_type": "uint16", "nodata": 0}],
                "proj:epsg": 32632,
                "proj:shape": [1024, 1024],
                "proj:transform": [10.0, 0.0, 500000.0, 0.0, -10.0, 5200000.0],
                "eo:bands": [{"name": "B04", "common_name": "red"}]
            }
        }
    }
    assert validate_item(item) is True
    captured = capsys.readouterr()
    assert "STAC Item Best Practice Warnings" not in captured.err

def test_get_valid_prefixes_and_dss_rules():
    """Test JWT token prefix extraction and DSS path validation."""
    token = {
        "preferred_username": "myuser",
        "groups": [
            "/dss/project-dss-group",
            "/dss/shared-dss-group-ro",
            "/dss/admin-dss-group-mgr", # should be skipped
            "/regular/group"           # should be skipped
        ]
    }
    
    # append_dot=True
    rw, ro = get_valid_prefixes(decoded_token=token, append_dot=True)
    assert rw == ["myuser.", "project-dss-group."]
    assert ro == ["shared-dss-group."]
    
    # append_dot=False
    rw_nodot, ro_nodot = get_valid_prefixes(decoded_token=token, append_dot=False)
    assert rw_nodot == ["myuser", "project-dss-group"]
    assert ro_nodot == ["shared-dss-group"]
    
    # DSS Collection prefix check in validate_item:
    # A DSS collection requires asset file:/// URLs to match prefix with dot
    item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "dss-item",
        "collection": "project-dss-group.collection",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v1.0.0/schema.json"],
        "assets": {
            "data": {"href": "file:///path/to/project-dss-group./file.tif"}
        }
    }
    assert validate_item(item) is True
    
    # Mismatch DSS prefix
    item["assets"]["data"]["href"] = "file:///path/to/other-group/file.tif"
    assert validate_item(item) is False

    # Standalone collection with no prefix and DSS file href fails if no tokens
    standalone_item = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "standalone-item",
        "collection": "noprefixcollection",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "bbox": [0, 0, 0, 0],
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "stac_extensions": ["https://stac-extensions.github.io/contacts/v1.0.0/schema.json"],
        "assets": {
            "data": {"href": "file:///dss/path/file.tif"}
        }
    }
    assert validate_item(standalone_item) is False
