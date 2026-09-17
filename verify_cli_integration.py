import sys
import os
import json
import jwt
import click
from unittest.mock import MagicMock, patch

# Add src to sys.path
sys.path.append(os.path.abspath("src"))

# Mock requests only
sys.modules['requests'] = MagicMock()

import terrapi.cli.stac_api_cli as stac_api_cli
from terrapi.private.stac import update_mandatory_fields

def test_cli_integration():
    # Setup click context
    obj = {'noAuth': False, 'privateAPIUrl': 'http://test', 'ClientId': 'test-client', 'DEBUG': True}
    ctx = click.Context(stac_api_cli.stac, obj=obj)
    
    payload = {"preferred_username": "cliuser", "email": "cliuser@example.com"}
    auth_token = jwt.encode(payload, "secret", algorithm="HS256")
    
    tokens = MagicMock()
    tokens.access_token = auth_token
    
    # Mock _get_auth_refresh_tokens and other helpers
    stac_api_cli._get_auth_refresh_tokens = MagicMock(return_value=tokens)
    stac_api_cli._get_json_response_from_signed_request = MagicMock(return_value={"status": "ok"})
    stac_api_cli._readJson_from_file_or_str = MagicMock()
    
    # Mock validation functions
    stac_api_cli.validate_collection = MagicMock(return_value=True)
    stac_api_cli.validate_item = MagicMock(return_value=True)

    with ctx:
        # Test Collection Create
        collection = {"type": "Collection", "id": "test-c"}
        stac_api_cli._readJson_from_file_or_str.return_value = collection
        
        stac_api_cli.create.callback(id="test-c", json_str="{}", inputfile=None, update=False, quiet=True)
        
        assert "contacts" in collection, "Contacts field missing from collection"
        assert collection["contacts"][0]["name"] == "cliuser"
        print("CLI Collection Create integration verified!")

        # Test Item Create
        item = {"type": "Feature", "id": "test-i", "properties": {}}
        stac_api_cli._readJson_from_file_or_str.return_value = item
        
        stac_api_cli.create_item.callback(collection_id="test-c", item_id="test-i", json_str="{}", inputfile=None, update=False, pretty=False, quiet=True)
        
        assert "contacts" in item["properties"], "Contacts field missing from item properties"
        assert item["properties"]["contacts"][0]["name"] == "cliuser"
        print("CLI Item Create integration verified!")

if __name__ == "__main__":
    try:
        test_cli_integration()
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
