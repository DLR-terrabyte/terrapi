from click import echo

from ..auth import RefreshTokenStore

def add_update_private_api_fields_item(item: dict,allways_set_created: bool=True) -> dict:
    """Add required fields to a STAC Item if they are missing.

    Args:
        item (dict): The JSON object representing the STAC Item."""
    item.