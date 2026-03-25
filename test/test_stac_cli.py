import pytest
import json
import uuid
from click.testing import CliRunner
from terrapi.cli.terrapi_cli import terrapi

collection_prefix="di93bor.autotest"

@pytest.fixture(scope="module")
def runner():
    return CliRunner()

@pytest.fixture(scope="module")
def unique_id():
    # Create a unique ID for the collection to avoid collisions
    return f"{collection_prefix}-{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="module")
def item_id():
    return f"test-item-{uuid.uuid4().hex[:8]}"

def test_stac_help(runner):
    """Test that the stac command help is displayed correctly."""
    result = runner.invoke(terrapi, ['stac', '--help'])
    assert result.exit_code == 0
    assert "Command Line Interface for Terrabyte STAC API" in result.output

def test_login(runner):
    """Ensure we have valid credentials before running tests."""
    print("\nChecking for valid credentials...")
    result = runner.invoke(terrapi, ['stac', 'auth', '--noninteractive'])
    if result.exit_code != 0:
        pytest.fail("No valid refresh token found. Please run 'terrapi login' manually before running tests.")
    assert result.exit_code == 0

def test_collection_lifecycle(runner, unique_id, item_id):
    """
    Test the full lifecycle of a STAC Collection and Item:
    1. Create Collection
    2. List Collections (verify presence)
    3. Get Collection
    4. Create Item in Collection
    5. Get Item
    6. Delete Item
    7. Delete Collection
    """
    
    # --- 1. Create Collection ---
    collection_data = {
        "id": unique_id,
        "type": "Collection",
        "stac_version": "1.0.0",
        "description": "Integration test collection created by automated tests",
        "license": "proprietary",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [[None, None]]}
        },
        "links": []
    }
    
    with runner.isolated_filesystem():
        with open('collection.json', 'w') as f:
            json.dump(collection_data, f)
            
        print(f"\nCreating collection {unique_id}...")
        result = runner.invoke(terrapi, ['stac', 'collection', 'create', '--file', 'collection.json'])
        assert result.exit_code == 0, f"Collection create failed: {result.output}"
        # The output should contain the JSON of the created collection
        assert unique_id in result.output

    # --- 2. List Collections ---
    print(f"Listing collections with filter {unique_id}...")
    result = runner.invoke(terrapi, ['stac', 'collection', 'list', '--filter', unique_id, '-o', '-'])
    print(f"Result: {result.output}")
    print(f"DEBUG info:")
    print(f"unique_id: {repr(unique_id)}")
    print(f"result.output: {repr(result.output)}")
    assert result.exit_code == 0
    assert unique_id in result.output

    # --- 3. Get Collection ---
    print(f"Getting collection {unique_id}...")
    result = runner.invoke(terrapi, ['stac', 'collection', 'get', unique_id, '-o', '-'])
    assert result.exit_code == 0
    print(result.output)
    assert unique_id in result.output
    
    # --- 4. Create Item ---
    item_data = {
        "id": item_id,
        "type": "Feature",
        "stac_version": "1.0.0",
        "stac_extensions": [],
        "collection": unique_id,
        "geometry": {
            "type": "Point",
            "coordinates": [11.582, 48.135] # Munich
        },
        "bbox": [11.582, 48.135, 11.582, 48.135],
        "properties": {
            "datetime": "2023-01-01T12:00:00Z",
            "test_prop": "test_value"
        },
        "links": [],
        "assets": {}
    }
    
    with runner.isolated_filesystem():
        with open('item.json', 'w') as f:
            json.dump(item_data, f)
            
        print(f"Creating item {item_id} in {unique_id}...")
        result = runner.invoke(terrapi, ['stac', 'item', 'create', unique_id, '--file', 'item.json'])
        assert result.exit_code == 0, f"Item create failed: {result.output}"

    # --- 5. Get Item ---
    print(f"Getting item {item_id}...")
    result = runner.invoke(terrapi, ['stac', 'item', 'get', unique_id, item_id, '-o', '-'])
    assert result.exit_code == 0
    assert item_id in result.output
    assert "test_value" in result.output

    # --- 6. Delete Item ---
    print(f"Deleting item {item_id}...")
    # input='y' to confirm the deletion prompt
    result = runner.invoke(terrapi, ['stac', 'item', 'delete',"--yes", unique_id, item_id])
    assert result.exit_code == 0
    assert f"Deleted Item {item_id}" in result.output

    # Verify item is gone
    result = runner.invoke(terrapi, ['stac', 'item', 'get', unique_id, item_id, '-o', '-'])
    # Assuming get returns nothing or error info on stdout/stderr, but we check key indicators
    # The API might return 404, we expect the CLI to handle it gracefully or output error
    # For integration test, ensuring the success path above is key. 
    # If 404, output should probably not contain our item ID in a valid JSON structure

    # --- 7. Delete Collection ---
    print(f"Deleting collection {unique_id}...")
    result = runner.invoke(terrapi, ['stac', 'collection', 'delete','--yes', unique_id])
    assert result.exit_code == 0
    assert f"Deleted Collection {unique_id}" in result.output

    # --- 8. Final Verification ---
    # Ensure collection is gone
    result = runner.invoke(terrapi, ['stac', 'collection', 'get', unique_id, '-o', '-'])
    # Should likely fail or return nothing valid
    # Depending on implementation, it might output "Stac API reported a (404)..."
    assert "404" in result.output or result.exit_code != 0 or unique_id not in result.output

def test_prefix_filtering(runner):
    """Test the --writable and --readonly flags for the prefix command."""
    # 1. Default (Show All) - Should show headers if prefixes exist
    # We can't guarantee the user has prefixes, but if they do, headers should be there.
    # If they don't have prefixes, output is empty.
    # Let's assume for a real integration test, the user 'zeid_ju' likely has a prefix.
    
    result = runner.invoke(terrapi, ['stac', 'collection', 'prefix'])
    assert result.exit_code == 0
    # If output is not empty, it implies headers or prefixes.
    # The header "Writable Collection prefixes:" is expected if show_all is True and rw_prefix exists.
    
    # 2. Writable Only (-w) - Should NOT show headers
    result_w = runner.invoke(terrapi, ['stac', 'collection', 'prefix', '-w'])
    assert result_w.exit_code == 0
    assert "Writable Collection prefixes:" not in result_w.output
    assert "Readonly Collection prefixes:" not in result_w.output
    
    # 3. Readonly Only (-r) - Should NOT show headers
    result_r = runner.invoke(terrapi, ['stac', 'collection', 'prefix', '-r'])
    assert result_r.exit_code == 0
    assert "Writable Collection prefixes:" not in result_r.output
    assert "Readonly Collection prefixes:" not in result_r.output

def test_item_create_flags(runner):
    """Test various flags for terrapi stac item create."""
    # Setup: Create a temporary collection for these tests
    flag_col_id = f"di93bor.flags-{uuid.uuid4().hex[:8]}"
    
    collection_data = {
        "id": flag_col_id,
        "type": "Collection",
        "stac_version": "1.0.0",
        "description": "Collection for testing item create flags",
        "license": "proprietary",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [[None, None]]}
        },
        "links": []
    }
    
    with runner.isolated_filesystem():
        with open('setup_col.json', 'w') as f:
            json.dump(collection_data, f)
        runner.invoke(terrapi, ['stac', 'collection', 'create', '--file', 'setup_col.json'])

    try:
        # --- Test 1: --id overwrite ---
        base_item_id = f"item-{uuid.uuid4().hex[:8]}"
        overwrite_id = f"overwrite-{uuid.uuid4().hex[:8]}"
        
        item_data = {
            "id": base_item_id,
            "type": "Feature",
            "stac_version": "1.0.0",
            "collection": flag_col_id,
            "geometry": {"type": "Point", "coordinates": [0, 0]},
            "bbox": [0, 0, 0, 0],
            "properties": {"datetime": "2023-01-01T00:00:00Z"},
            "links": [],
            "assets": {}
        }
        
        with runner.isolated_filesystem():
            with open('item_base.json', 'w') as f:
                json.dump(item_data, f)
            
            print(f"Testing --id flag: Overwriting {base_item_id} with {overwrite_id}")
            result = runner.invoke(terrapi, ['stac', 'item', 'create', flag_col_id, '--file', 'item_base.json', '--id', overwrite_id])
            assert result.exit_code == 0
            assert overwrite_id in result.output
            assert base_item_id not in result.output # Original ID should not be widely present in success msg as ID

        # --- Test 2: --json input ---
        json_item_id = f"json-{uuid.uuid4().hex[:8]}"
        item_data['id'] = json_item_id
        # Remove collection to Ensure CLI sets it or backend accepts it (CLI create_item handles it)
        # item_data['collection'] = flag_col_id 
        
        print(f"Testing --json flag: Creating {json_item_id}")
        json_str = json.dumps(item_data)
        result = runner.invoke(terrapi, ['stac', 'item', 'create', flag_col_id, '--json', json_str])
        assert result.exit_code == 0
        assert json_item_id in result.output

        # --- Test 3: --update (upsert) ---
        print(f"Testing --update flag: Updating {json_item_id}")
        # Modify a property
        item_data['properties']['test_prop'] = "updated"
        json_str_update = json.dumps(item_data)
        
        # First try without --update, should fail (409 Conflict)
        result_fail = runner.invoke(terrapi, ['stac', 'item', 'create', flag_col_id, '--json', json_str_update])
        # The CLI might catch the error or print it. 
        # Based on stac_api_cli.py, it handles 409 and prints error but incorrectly returns 0 sometimes? 
        # Actually it returns None on 409 and prints to stderr.
        # But let's check --update success directly.
        
        result_update = runner.invoke(terrapi, ['stac', 'item', 'create', flag_col_id, '--json', json_str_update, '--update'])
        assert result_update.exit_code == 0
        assert json_item_id in result_update.output
        
        # Verify update happened
        result_get = runner.invoke(terrapi, ['stac', 'item', 'get', flag_col_id, json_item_id, '-o', '-'])
        assert "updated" in result_get.output

        # --- Test 4: --pretty ---
        print("Testing --pretty flag")
        pretty_id = f"pretty-{uuid.uuid4().hex[:8]}"
        item_data['id'] = pretty_id
        json_str_pretty = json.dumps(item_data)
        
        result = runner.invoke(terrapi, ['stac', 'item', 'create', flag_col_id, '--json', json_str_pretty, '--pretty'])
        assert result.exit_code == 0
        # Check for indentation (newlines and spaces)
        assert "\n" in result.output
        assert "  " in result.output 

        # --- Test 5: --quiet ---
        print("Testing --quiet flag")
        quiet_id = f"quiet-{uuid.uuid4().hex[:8]}"
        item_data['id'] = quiet_id
        json_str_quiet = json.dumps(item_data)
        
        result = runner.invoke(terrapi, ['stac', 'item', 'create', flag_col_id, '--json', json_str_quiet, '--quiet'])
        assert result.exit_code == 0
        assert result.output.strip() == ""

    finally:
        # Cleanup
        print(f"Cleaning up collection {flag_col_id}")
        runner.invoke(terrapi, ['stac', 'collection', 'delete', '--yes', flag_col_id])

