import re
import click
import jwt
from ..util import rfc3339

# --- From validate.py ---

# Define the regex for valid IDs (based on pgstac fastapi rules)
VALID_ID_REGEX = r"^[a-zA-Z0-9_\-\.]{1,255}$"

# Latest STAC Extension versions
LATEST_EXTENSIONS = {
    "contacts": "https://stac-extensions.github.io/contacts/v1.0.0/schema.json",
    "raster": "https://stac-extensions.github.io/raster/v2.0.0/schema.json",
    "projection": "https://stac-extensions.github.io/projection/v2.0.0/schema.json",
    "eo": "https://stac-extensions.github.io/eo/v2.0.0/schema.json",
}

REQUIRED_EXTENSIONS = [
    LATEST_EXTENSIONS["contacts"]
]

RECOMMENDED_EXTENSIONS = [
    LATEST_EXTENSIONS["raster"],
    LATEST_EXTENSIONS["projection"],
    LATEST_EXTENSIONS["eo"]
]

def parse_extension_info(ext_url: str):
    """Extract (extension_name, version_string) from a STAC extension schema URL."""
    if not isinstance(ext_url, str):
        return None, None
    match = re.search(r"stac-extensions\.github\.io/([^/]+)/v?([^/]+)", ext_url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def parse_version_tuple(ver_str: str):
    """Parse version string into a tuple of integers for comparison."""
    clean_ver = ver_str.lstrip("v")
    parts = re.findall(r"\d+", clean_ver)
    return tuple(int(p) for p in parts) if parts else (0,)

def is_version_older(current_ver: str, latest_ver: str) -> bool:
    """Return True if current_ver is strictly older than latest_ver."""
    return parse_version_tuple(current_ver) < parse_version_tuple(latest_ver)

def check_extension_versions(stac_extensions: list) -> list[str]:
    """Return list of warning strings for any stac_extensions using an older version."""
    warnings = []
    if not isinstance(stac_extensions, list):
        return warnings
    for ext_url in stac_extensions:
        ext_name, current_ver = parse_extension_info(ext_url)
        if ext_name and ext_name in LATEST_EXTENSIONS:
            latest_url = LATEST_EXTENSIONS[ext_name]
            _, latest_ver = parse_extension_info(latest_url)
            if current_ver and latest_ver and is_version_older(current_ver, latest_ver):
                warnings.append(
                    f"Best Practice: STAC extension '{ext_name}' version '{current_ver}' is older than recommended version '{latest_ver}' ({latest_url})."
                )
    return warnings

def validate_id(id_value: str, id_type: str = "ID") -> bool:
    """Validate if an ID conforms to pgstac fastapi restrictions."""
    if not re.match(VALID_ID_REGEX, id_value):
        click.echo(f"Invalid {id_type}: '{id_value}'. IDs must be alphanumeric and can include '_', '-', or '.'. Maximum length is 255 characters.", err=True)
        return False
    return True

def validate_extensions(item_or_collection: dict, required_extensions: list) -> bool:
    """Validate if the required STAC extensions are included."""
    errors = []
    extensions = item_or_collection.get("stac_extensions", [])

    if not isinstance(extensions, list):
        errors.append("Invalid 'stac_extensions': Must be a list.")
    else:
        for req_ext in required_extensions:
            req_name, _ = parse_extension_info(req_ext)
            found = False
            for ext in extensions:
                if ext == req_ext:
                    found = True
                    break
                ext_name, _ = parse_extension_info(ext)
                if req_name and ext_name == req_name:
                    found = True
                    break
            if not found:
                errors.append(f"Missing required STAC extension: {req_ext}")

    if errors:
        click.echo("STAC Extensions validation failed with the following errors:", err=True)
        for error in errors:
            click.echo(f"- {error}", err=True)
        return False
    return True

def validate_item(item: dict, auth_token: str = None, decoded_token: dict = None, skip_asset_validation: bool = False) -> bool:
    """Validate if a JSON object conforms to minimal STAC Item or FeatureCollection requirements."""
    if item.get("type") == "FeatureCollection":
        errors = []
        warnings = []
        if "features" not in item or not isinstance(item["features"], list):
            errors.append("Invalid FeatureCollection: Missing or invalid 'features' field.")
        else:
            for index, feature in enumerate(item["features"]):
                # Recursive call now needs to handle both errors and warnings
                # But for simplicity, we let the inner call print its own warnings
                if not validate_item(feature, auth_token=auth_token, decoded_token=decoded_token, skip_asset_validation=skip_asset_validation):
                    errors.append(f"Feature at index {index} is invalid.")
        if errors:
            click.echo("FeatureCollection validation failed with the following errors:", err=True)
            for error in errors:
                click.echo(f"- {error}", err=True)
            return False
        return True

    # Validate as single STAC Item
    required_fields = ["stac_version", "type", "id", "geometry", "bbox", "properties", "assets"]
    # Terrabyte required extensions
    required_extensions = REQUIRED_EXTENSIONS
    # ODC STAC recommended extensions
    recommended_extensions = RECOMMENDED_EXTENSIONS
    errors = []
    warnings = []

    for field in required_fields:
        if field not in item:
            errors.append(f"Missing required field: {field}")

    if item.get("type") != "Feature":
        errors.append(f"Invalid 'type': {item.get('type')}. Expected 'Feature'.")

    item_id = item.get("id")
    if not item_id or not validate_id(item_id, "Item ID"):
        errors.append(f"Invalid 'id': {item_id}")

    if not isinstance(item.get("geometry"), dict):
        errors.append("Invalid 'geometry': Must be a GeoJSON object.")

    if not isinstance(item.get("bbox"), list) or len(item["bbox"]) != 4:
        errors.append("Invalid 'bbox': Must be a list of 4 coordinates (xmin, ymin, xmax, ymax).")

    if not isinstance(item.get("properties"), dict):
        errors.append("Invalid 'properties': Must be a dictionary.")

    if not isinstance(item.get("assets"), dict) or not item["assets"]:
        errors.append("Invalid 'assets': Must be a non-empty dictionary.")
    elif not skip_asset_validation:
        # Asset URL validation
        collection_id = item.get("collection")
        prefix = collection_id.split(".")[0] if collection_id and "." in collection_id else None
        
        # Determine allowed prefixes
        allowed_prefixes = []
        if prefix:
            if "dss" in prefix:
                # DSS prefix: Must match specifically
                allowed_prefixes = [prefix + "."]
            else:
                # Non-DSS prefix: Can be any allowed prefix for the user
                if auth_token or decoded_token:
                    rw, ro = get_valid_prefixes(auth_token=auth_token, decoded_token=decoded_token, append_dot=False)
                    allowed_prefixes = rw + ro
                else:
                    # Fallback to the collection's own prefix if no token is available
                    allowed_prefixes = [prefix]

        for asset_key, asset_val in item["assets"].items():
            href = asset_val.get("href", "")
            if not href:
                errors.append(f"Asset '{asset_key}' is missing 'href'.")
                continue
                
            if not (href.startswith("http://") or href.startswith("https://") or href.startswith("file://")):
                errors.append(f"Asset '{asset_key}' has invalid URL scheme: '{href}'. Must be http://, https://, or file://.")
            elif href.startswith("file:///"):
                # Check absolute file URL against allowed prefixes
                if not allowed_prefixes:
                    # If no prefix in collection ID and no tokens, we can't strictly enforce but we should warn if it looks like a DSS path
                    if "/dss/" in href:
                         errors.append(f"Asset '{asset_key}' uses a DSS file URL, but no valid prefixes could be determined for validation.")
                elif not any(p in href for p in allowed_prefixes):
                    if len(allowed_prefixes) == 1:
                        errors.append(f"Asset '{asset_key}' absolute file URL '{href}' does not contain the required prefix '{allowed_prefixes[0]}' from the collection ID.")
                    else:
                        errors.append(f"Asset '{asset_key}' absolute file URL '{href}' does not contain any of the allowed prefixes: {allowed_prefixes}")

    if not validate_extensions(item, required_extensions):
        errors.append("Missing required STAC extensions.")

    # --- Best Practice Checks (Warnings) ---
    stac_extensions = item.get("stac_extensions", [])
    
    # Check for recommended extensions
    for rec_ext in recommended_extensions:
        rec_name, _ = parse_extension_info(rec_ext)
        found = False
        for ext in stac_extensions:
            if ext == rec_ext:
                found = True
                break
            ext_name, _ = parse_extension_info(ext)
            if rec_name and ext_name == rec_name:
                found = True
                break
        if not found:
            warnings.append(f"Best Practice: Missing recommended STAC extension: {rec_ext}")

    # Check for older extension versions
    warnings.extend(check_extension_versions(stac_extensions))

    assets = item.get("assets", {})
    if isinstance(assets, dict):
        has_raster = any(parse_extension_info(ext)[0] == "raster" for ext in stac_extensions if isinstance(ext, str))
        has_proj = any(parse_extension_info(ext)[0] == "projection" for ext in stac_extensions if isinstance(ext, str))
        has_eo = any(parse_extension_info(ext)[0] == "eo" for ext in stac_extensions if isinstance(ext, str))

        for asset_key, asset_val in assets.items():
            if not isinstance(asset_val, dict):
                continue
            # Raster best practices
            if has_raster:
                raster_bands = asset_val.get("raster:bands", [])
                if not raster_bands:
                    warnings.append(f"Best Practice: Asset '{asset_key}' is missing 'raster:bands' while using raster extension.")
                else:
                    for i, band in enumerate(raster_bands):
                        if "data_type" not in band:
                            warnings.append(f"Best Practice: Asset '{asset_key}' band {i} is missing 'data_type'.")
                        if "nodata" not in band:
                            warnings.append(f"Best Practice: Asset '{asset_key}' band {i} is missing 'nodata'.")

            # Projection best practices
            if has_proj:
                for field in ["proj:epsg", "proj:shape", "proj:transform"]:
                    if field not in asset_val and field not in item.get("properties", {}):
                        warnings.append(f"Best Practice: Missing '{field}' for asset '{asset_key}' (or in item properties).")

            # EO best practices
            if has_eo:
                eo_bands = asset_val.get("eo:bands", [])
                if not eo_bands:
                    warnings.append(f"Best Practice: Asset '{asset_key}' is missing 'eo:bands' while using eo extension.")
                else:
                    for i, band in enumerate(eo_bands):
                        if "common_name" not in band:
                            warnings.append(f"Best Practice: Asset '{asset_key}' band {i} is missing 'common_name'.")

    if warnings:
        click.echo("STAC Item Best Practice Warnings:", err=True)
        for warning in warnings:
            click.echo(f"  [WARN] {warning}", err=True)

    if errors:
        click.echo("STAC Item validation failed with the following errors:", err=True)
        for error in errors:
            click.echo(f"- {error}", err=True)
        return False
    return True

def validate_collection(collection: dict) -> bool:
    """Validate if a JSON object conforms to minimal STAC Collection requirements."""
    required_fields = ["stac_version", "type", "id", "extent", "license", "description"]
    required_extensions = REQUIRED_EXTENSIONS
    errors = []
    warnings = []

    for field in required_fields:
        if field not in collection:
            errors.append(f"Missing required field: {field}")

    if collection.get("type") != "Collection":
        errors.append(f"Invalid 'type': {collection.get('type')}. Expected 'Collection'.")

    collection_id = collection.get("id")
    if not collection_id or not validate_id(collection_id, "Collection ID"):
        errors.append(f"Invalid 'id': {collection_id}")

    if not isinstance(collection.get("extent"), dict):
        errors.append("Invalid 'extent': Must be a dictionary.")

    if not validate_extensions(collection, required_extensions):
        errors.append("Missing required STAC extensions.")

    # --- Best Practice Checks (Warnings) ---
    stac_extensions = collection.get("stac_extensions", [])
    warnings.extend(check_extension_versions(stac_extensions))

    if warnings:
        click.echo("STAC Collection Best Practice Warnings:", err=True)
        for warning in warnings:
            click.echo(f"  [WARN] {warning}", err=True)

    if errors:
        click.echo("STAC Collection validation failed with the following errors:", err=True)
        for error in errors:
            click.echo(f"- {error}", err=True)
        return False
    return True

# --- From private_api_prefixes.py ---

def get_valid_prefixes(auth_token: str = None, decoded_token: dict = None, append_dot: bool = True) -> tuple[list[str], list[str]]:
    """Determine valid read/write and read-only prefixes from JWT token."""
    if not decoded_token:
        if not auth_token:
            return [], []
        decoded_token = jwt.decode(auth_token, options={"verify_signature": False})
    
    decoded = decoded_token
    rw_prefix = []
    ro_prefix = []
    user_id = decoded.get("preferred_username")
    
    suffix = "." if append_dot else ""
    
    if user_id:
        rw_prefix.append(user_id + suffix)
    groups = decoded.get("groups")
    if groups:
        for g in groups:
            if g.startswith("/dss/"):
                g = g.replace("/dss/", "")
                if "-dss-" in g and not g.endswith("-mgr"):
                    if g.endswith("-ro"):
                        p = g.replace("-ro", "")
                        ro_prefix.append(p + suffix)
                    else:
                        rw_prefix.append(g + suffix)
        rw_prefix.sort()
        ro_prefix.sort()
    return rw_prefix, ro_prefix

# --- From required.py ---

def update_mandatory_fields(item: dict, auth_token: str = None, allways_set_created: bool = False, decoded_token: dict = None) -> dict:
    """Add required fields to a STAC Item, FeatureCollection, or Collection if they are missing."""
    if not decoded_token:
        if not auth_token:
            return item
        decoded_token = jwt.decode(auth_token, options={"verify_signature": False})

    if item.get("type") == "FeatureCollection":
        features = item.get("features", [])
        for feature in features:
            update_mandatory_fields(feature, allways_set_created=allways_set_created, decoded_token=decoded_token)
        return item

    # Use decoded JWT to get user info
    username = decoded_token.get("preferred_username")
    email = decoded_token.get("email")

    # Ensure stac_extensions exists
    if "stac_extensions" not in item:
        item["stac_extensions"] = []

    # Add Contacts Extension if missing or update older version
    contact_ext = LATEST_EXTENSIONS["contacts"]
    has_contacts = False
    for i, ext in enumerate(item["stac_extensions"]):
        name, ver = parse_extension_info(ext)
        if name == "contacts" or ext == contact_ext:
            has_contacts = True
            if ext != contact_ext:
                item["stac_extensions"][i] = contact_ext
            break
    if not has_contacts:
        item["stac_extensions"].append(contact_ext)

    # Set contacts information
    contact = {"roles": ["contact"]}
    if username:
        contact["name"] = username
    if email:
        contact["emails"] = [email]
    
    # Determine where to put fields based on type
    is_collection = item.get("type") == "Collection"
    target = item if is_collection else item.setdefault("properties", {})

    target["contacts"] = [contact]

    # Set created and updated fields
    now = rfc3339.utcnow()
    target["updated"] = now
    if allways_set_created or "created" not in target:
        target["created"] = now

    return item

