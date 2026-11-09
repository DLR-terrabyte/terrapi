import pytest
from terrapi.private.stac import validate_item, validate_collection, update_mandatory_fields

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
    """Test that mandatory fields are correctly injected."""
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

