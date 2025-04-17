import re
import click
import traceback


def handle_error(ctx: dict, message: str, exit_code: int = 1, exception: Exception = None):
    """Handle errors consistently across the CLI.

    Args:
        ctx (dict): The Click context object.
        message (str): The error message to display.
        exit_code (int): The exit code for the program (default: 1).
        exception (Exception, optional): The exception object for debugging (default: None).
    """
    click.echo(f"Error: {message}", err=True)
    if ctx.obj.get('DEBUG') and exception:
        click.echo(f"Debug Info: {type(exception).__name__} at line {exception.__traceback__.tb_lineno} of {__file__}: {exception}", err=True)
        traceback.print_exc()
    exit(exit_code)


def validate_bbox_exit_error(ctx, bbox: list[float], errorcode: int = 1) -> bool:
    """Validate the bounding box format."""
    if bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
        handle_error(ctx, "Error: Invalid bounding box coordinates. xmin must be less than xmax and ymin must be less than ymax.", errorcode)
        return False
    if bbox[0] < -180 or bbox[2] > 180 or bbox[1] < -90 or bbox[3] > 90:
        handle_error(ctx, "Error: Bounding box coordinates must be within the range of [-180, 180] for longitude and [-90, 90] for latitude.", errorcode)
        return False
    return True


# Define the regex for valid IDs (based on pgstac fastapi rules)
VALID_ID_REGEX = r"^[a-zA-Z0-9_\-\.]{1,255}$"

def validate_id(id_value: str, id_type: str = "ID") -> bool:
    """Validate if an ID conforms to pgstac fastapi restrictions.

    Args:
        id_value (str): The ID to validate.
        id_type (str): The type of ID being validated (e.g., "Collection ID", "Item ID").

    Returns:
        bool: True if the ID is valid, False otherwise.
    """
    if not re.match(VALID_ID_REGEX, id_value):
        click.echo(f"Invalid {id_type}: '{id_value}'. IDs must be alphanumeric and can include '_', '-', or '.'. Maximum length is 255 characters.", err=True)
        return False
    return True


def validate_stac_extensions(item_or_collection: dict, required_extensions: list) -> bool:
    """Validate if the required STAC extensions are included in the stac_extensions field.

    Args:
        item_or_collection (dict): The JSON object representing the STAC Item or Collection.
        required_extensions (list): A list of required STAC extensions.

    Returns:
        bool: True if all required extensions are present, False otherwise.
    """
    errors = []
    extensions = item_or_collection.get("stac_extensions", [])

    if not isinstance(extensions, list):
        errors.append("Invalid 'stac_extensions': Must be a list.")
    else:
        for ext in required_extensions:
            if ext not in extensions:
                errors.append(f"Missing required STAC extension: {ext}")

    if errors:
        click.echo("STAC Extensions validation failed with the following errors:", err=True)
        for error in errors:
            click.echo(f"- {error}", err=True)
        return False

    return True


def validate_stac_item_or_collection(item: dict) -> bool:
    """Validate if a JSON object conforms to minimal STAC Item or FeatureCollection requirements.

    Args:
        item (dict): The JSON object representing the STAC Item or FeatureCollection.

    Returns:
        bool: True if the item or collection is valid, False otherwise.
    """
    errors = []

    # Check if the input is a FeatureCollection
    if item.get("type") == "FeatureCollection":
        if "features" not in item or not isinstance(item["features"], list):
            errors.append("Invalid FeatureCollection: Missing or invalid 'features' field.")
        else:
            for index, feature in enumerate(item["features"]):
                if not validate_stac_item(feature):
                    errors.append(f"Feature at index {index} is invalid.")
        if errors:
            click.echo("FeatureCollection validation failed with the following errors:", err=True)
            for error in errors:
                click.echo(f"- {error}", err=True)
            return False
        return True

    # Validate as a single STAC Item
    return validate_stac_item(item)


def validate_stac_item(item: dict) -> bool:
    """Validate if a JSON object conforms to minimal STAC Item requirements.

    Args:
        item (dict): The JSON object representing the STAC Item.

    Returns:
        bool: True if the item is valid, False otherwise.
    """
    required_fields = ["type", "id", "geometry", "bbox", "properties", "assets"]
    required_extensions = [
        "https://stac-extensions.github.io/raster/v1.1.0/schema.json",
        "https://stac-extensions.github.io/projection/v1.0.0/schema.json"
    ]
    errors = []

    # Check if all required fields are present
    for field in required_fields:
        if field not in item:
            errors.append(f"Missing required field: {field}")

    # Validate the "type" field
    if item.get("type") != "Feature":
        errors.append(f"Invalid 'type': {item.get('type')}. Expected 'Feature'.")

    # Validate "id"
    item_id = item.get("id")
    if not item_id or not validate_id(item_id, "Item ID"):
        errors.append(f"Invalid 'id': {item_id}")

    # Validate "geometry"
    if not isinstance(item.get("geometry"), dict):
        errors.append("Invalid 'geometry': Must be a GeoJSON object.")

    # Validate "bbox"
    if not isinstance(item.get("bbox"), list) or len(item["bbox"]) != 4:
        errors.append("Invalid 'bbox': Must be a list of 4 coordinates (xmin, ymin, xmax, ymax).")

    # Validate "properties"
    if not isinstance(item.get("properties"), dict):
        errors.append("Invalid 'properties': Must be a dictionary.")

    # Validate "assets"
    if not isinstance(item.get("assets"), dict) or not item["assets"]:
        errors.append("Invalid 'assets': Must be a non-empty dictionary.")

    # Validate required STAC extensions
    if not validate_stac_extensions(item, required_extensions):
        errors.append("Missing required STAC extensions.")

    # Print errors if any
    if errors:
        click.echo("STAC Item validation failed with the following errors:", err=True)
        for error in errors:
            click.echo(f"- {error}", err=True)
        return False

    return True


def validate_stac_collection(collection: dict) -> bool:
    """Validate if a JSON object conforms to minimal STAC Collection requirements.

    Args:
        collection (dict): The JSON object representing the STAC Collection.

    Returns:
        bool: True if the collection is valid, False otherwise.
    """
    required_fields = ["type", "id", "extent"]
    required_extensions = [
        "https://stac-extensions.github.io/raster/v1.1.0/schema.json",
        "https://stac-extensions.github.io/projection/v1.0.0/schema.json"
    ]
    errors = []

    # Check if all required fields are present
    for field in required_fields:
        if field not in collection:
            errors.append(f"Missing required field: {field}")

    # Validate the "type" field
    if collection.get("type") != "Collection":
        errors.append(f"Invalid 'type': {collection.get('type')}. Expected 'Collection'.")

    # Validate "id"
    collection_id = collection.get("id")
    if not collection_id or not validate_id(collection_id, "Collection ID"):
        errors.append(f"Invalid 'id': {collection_id}")

    # Validate "extent"
    if not isinstance(collection.get("extent"), dict):
        errors.append("Invalid 'extent': Must be a dictionary.")

    # Validate required STAC extensions
    if not validate_stac_extensions(collection, required_extensions):
        errors.append("Missing required STAC extensions.")

    # Print errors if any
    if errors:
        click.echo("STAC Collection validation failed with the following errors:", err=True)
        for error in errors:
            click.echo(f"- {error}", err=True)
        return False

    return True
