import click
import json
import re
import jwt
import traceback
from typing import Tuple, TextIO
import requests


from ..settings import  TERRABYTE_PUBLIC_API_URL



from ..adapter import wrap_request
from .shared_cli import login, auth, _get_auth_refresh_tokens, _readJson_from_file_or_str
from ..stac_validation import validate_bbox_exit_error, validate_stac_item_or_collection, validate_stac_item ,handle_error

def _get_next_url(links)->str|None:
    if links:
        for link in links:
            if link['rel']=='next':
                return link['href']
    return None

def _get_json_response_from_signed_request_paging(ctx:dict,stac_path:str, error_desc:str, method="GET",alt_method: str = None,alt_code:int =-1,maxElements=None, **kwargs)->dict:
    json_stac=_get_json_response_from_signed_request(ctx, stac_path, error_desc, method,alt_method,alt_code, **kwargs)
    if json_stac and json_stac.get("type")=="FeatureCollection":
        nexUrl=_get_next_url(json_stac.get('links'))
        while nexUrl:
            extra_stac=_get_json_response_from_signed_url(ctx,nexUrl, error_desc, method,alt_method,alt_code, **kwargs)
            if extra_stac:
                nexUrl=_get_next_url(extra_stac.get('links'))
                if ctx.obj['DEBUG']:
                    click.echo(f"nextURL is {nexUrl}")
                json_stac['features'].extend(extra_stac.get('features', None))
                json_stac['context']['limit']+=extra_stac['context']['limit']
                if maxElements:
                    if json_stac['context']['limit']>=maxElements:
                        nexUrl=None
            else:
                nexUrl=None
        #remove next ling as we iterated over next links to download all items
        json_stac['links']=[link for link in json_stac['links'] if link['rel']!='next']
    return json_stac

def construct_url(ctx: dict, path: str) -> str:
    """Construct the appropriate URL based on the context."""
    base_url = ctx.obj['publicStacUrl'] if ctx.obj['noAuth'] else ctx.obj['privateAPIUrl']
    return f"{base_url}/{path}"


def _get_json_response_from_signed_request(ctx:dict,stac_path:str, error_desc:str, method="GET",alt_method: str = None,alt_code:int =-1,alt_path=None, **kwargs)->dict:
    url=construct_url(ctx,stac_path)
    if alt_path:
        alt_url=construct_url(ctx,alt_path)
    else:
        alt_url=None
    return(_get_json_response_from_signed_url(ctx,url, error_desc, method,alt_method,alt_code,alt_url, **kwargs))





def _get_json_response_from_signed_url(ctx:dict,url:str, error_desc:str, method="GET",alt_method: str = None,alt_code:int =-1, alt_url=None,noAuth: bool=False,**kwargs)->dict:
    debugCli =ctx.obj['DEBUG']
    if debugCli:
        click.echo(f" Requesting {error_desc} from {url} using {method} and providing {kwargs}", err=True)
    try:   
        if ctx.obj['noAuth']: 
            r = requests.request(url=url, method=method, **kwargs)
        else:  
            r=wrap_request(requests.sessions.Session(),url=url,client_id=ctx.obj['ClientId'],method=method,**kwargs)      
        #check if request was successful 
        # see https://github.com/stac-utils/stac-fastapi/blob/add05de82f745a717b674ada796db0e9f7153e27/stac_fastapi/api/stac_fastapi/api/errors.py#L23
        # https://stac.terrabyte.lrz.de/public/api/api.html#/
        # https://eoapi.develop.eoepca.org/stac/api.html
        #fastAPI errors:
        if alt_method and r.status_code == alt_code :
            if debugCli:
                click.echo(f"Request to {url} using {method} failed with error Code 409. Retrying with  {alt_method}",err=True)
            if not alt_url:
                alt_url=url
        
            if ctx.obj['noAuth']:                
                r2= requests.request(url=alt_url, method=alt_method, **kwargs)
            else:  
                r2=wrap_request(requests.sessions.Session(),url=alt_url,client_id=ctx.obj['ClientId'],method=alt_method,**kwargs)
            #if alt request was succesful switch to it
            if 200<=r2.status_code<=299:
                r=r2
                method=alt_method
                url=alt_url
        json_stac={}
        try:
            json_stac=r.json()
        except Exception as e:
            if debugCli:
                click.echo("Caught Exception in converting Response to JSON")
                click.echo(e)
                click.echo(f"response was: {r.text}")
                click.echo(f"status Code:{r.status_code}")
                click.echo("Injecting empty json")
        
        message=json_stac.get('message', json_stac)

        match r.status_code:
            case 400:
                click.echo(f"Stac API reported a Bad Request ({r.status_code}) when calling {url}, Message: {message}", err=True)
                return None
            case 409:
                click.echo(f"Stac API reported a Conflict ({r.status_code}) while requesting {error_desc} when calling {url}. This can occur when the creation of an existing Collection or Item is requested or when  update is called on a non exiting Collection/Item.",err=True)
                return None
            case 422:
                message=json_stac.get('message', None)
                click.echo(f"Stac API reported a Validation Error ({r.status_code}) when calling {url}, Message: {message}", err=True)
                return None
            case 404:
                 code=json_stac.get('code', None)
                 click.echo(f"Stac API reported a ({r.status_code}) with {code} when calling {url}.", err=True)
                 if debugCli: 
                     click.echo(f"Response was: {json_stac}")
                 return None
            case 424:
                
                click.echo(f"Stac API reported a Database Error ({r.status_code}) when calling {url}, Message: {message}", err=True)
                return None
            case 500:
                click.echo(f"Stac API reported an Internal Server Error ({r.status_code}) when calling {url}, Message: {message}", err=True)
                click.echo(" Please retry again in a few Minutes and please report the issue to the terrabyte supportdesk if it persists.", err=True)
                return None        
        r.raise_for_status()
        return json_stac
       
    except Exception as e:
        click.echo(f"Requesting {error_desc} from URL {url} with Method {method} failed unexpectedly. Error Description  from Backend was{message}", err=True)
        if debugCli:
            click.echo("Error reported was:")
            click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            traceback.print_exc()
        return None


def _filterItemStripHref(item:dict, href_only:bool=False, strip_file:bool=False, assetfilter:list=None)->Tuple[dict,list]:
    assets=item.get('assets',[])
    new_assets={}
    hrefs=[]
    for name,asset in assets.items():
        if assetfilter and name not in assetfilter:
            continue  
        href=asset.get('href')
        if strip_file and href:
            href=href.replace("file://","",1)                       
            asset['href']=href
        hrefs.append(href)
        new_assets.update({name:asset})
    item.update({'assets':new_assets})
    return item,hrefs



def _get_valid_prefixes(auth_token):
    decoded = jwt.decode(auth_token, options={"verify_signature": False})
    rw_prefix = []
    ro_prefix = []
    user_id=decoded.get("preferred_username")
    groups=decoded.get("groups")
    if groups:
        for g in groups:
            if g.startswith("/dss/"):
                g = g.replace("/dss/","")
                if "-dss-" in g and not g.endswith("-mgr"):
                    if g.endswith("-ro"):
                        ro_prefix.append(g.replace("-ro","."))
                    else:
                        rw_prefix.append(g+".") 
        rw_prefix.sort()
        ro_prefix.sort()
    if user_id:
        rw_prefix.insert(0, user_id+".")
    return rw_prefix, ro_prefix


#end helper function now come the click commands

@click.group()
@click.option("-p", "--public", default=False, is_flag=True, show_default=False, help="Switch to public API for read-only access.")
@click.option("--privateURL", "private_url", type=str, show_default=False, default=None, help="Override private STAC API URL. (Expert option)")
@click.option("--publicURL", "public_url", type=str, show_default=False, default=None, help="Override public STAC API URL. (Expert option)")
@click.option("--clientID", "client_id", type=str, default=None, help="Override client ID. (Expert option)", hidden=True)
@click.pass_context
def stac(ctx: dict, public: bool = False, private_url: str = None, public_url: str = None, client_id: str = None):
    """Command Line Interface for Terrabyte STAC API.

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
    """
    if private_url:
        ctx.obj['privateAPIUrl'] = private_url
        if ctx.obj['DEBUG']:
            click.echo(f"Private API URL set to {private_url}")

    if public_url:
        ctx.obj['publicStacUrl'] = public_url
        public = True
        if ctx.obj['DEBUG']:
            click.echo(f"Public API URL set to {public_url}")
    else:
        ctx.obj['publicStacUrl'] = TERRABYTE_PUBLIC_API_URL

    ctx.obj['noAuth'] = public
    if public and ctx.obj['DEBUG']:
        click.echo("Switched to public STAC API. Update/modify operations are not allowed.")
        click.echo(f"Public API URL: {ctx.obj['publicStacUrl']}")

    if client_id:
        if ctx.obj['DEBUG']:
            click.echo(f"Client ID set to {client_id}")
        ctx.obj['ClientId'] = client_id


@click.group()
@click.pass_context
def collection(ctx: dict):
    """Manage STAC Collections.

    Collections are groups of related geospatial data items. This command group allows you to:
    - List collections.
    - Create, update, or delete collections.
    - Retrieve metadata for a specific collection.

    Examples:
    - List collections: `terrapi stac collection list`
    - Create a collection: `terrapi stac collection create --file collection.json`
    - Delete a collection: `terrapi stac collection delete <collection_id>`
    """
    pass


@click.group()
@click.pass_context
def item(ctx: dict):
    """Manage STAC Items.

    Items are individual geospatial data records within a collection. This command group allows you to:
    - List items in a collection.
    - Create, update, or delete items.
    - Retrieve metadata for a specific item.

    Examples:
    - List items: `terrapi stac item list <collection_id>`
    - Create an item: `terrapi stac item create <collection_id> --file item.json`
    - Delete an item: `terrapi stac item delete <collection_id> <item_id>`
    """
    pass


@collection.command()
@click.option("-f", "--filter", type=str, default="", help="Filter collections by ID using a regular expression.")
@click.option("-t", "--title", default=False, is_flag=True, help="Include collection titles in the output.")
@click.option("-d", "--description", default=False, is_flag=True, help="Include collection descriptions in the output.")
@click.option("-a", "--all", default=False, is_flag=True, help="Output the full JSON for each collection.")
@click.option("-p", "--pretty", default=False, is_flag=True, help="Pretty-print JSON output.")
@click.option("-o", "--outfile", type=click.File('w', encoding='utf8'), default=click.get_text_stream('stdout'), help="Write output to a file instead of stdout.")
@click.pass_context
def list(ctx: dict, outfile, filter: str = "", title: bool = False, description: bool = False, all: bool = False, pretty: bool = False):
    """List STAC Collections.

    Retrieve and display metadata for all available STAC collections. You can filter collections by ID, include additional metadata fields, or output the full JSON.

    Examples:
    - List all collections: `terrapi stac collection list`
    - Filter collections by ID: `terrapi stac collection list --filter "landsat.*"`
    - Output full JSON: `terrapi stac collection list --all`
    """
    indent = 2 if pretty else 0
    # Validate regex pattern if filter is provided
    if filter:
        # Replace leading * with .* for more intuitive filtering
        if filter.startswith('*'):
            filter = '.' + filter
        try:
            re.compile(filter)
        except re.error as e:
            click.echo(f"Error: Invalid regular expression '{filter} \n Please see https://docs.python.org/3/library/re.html for correct python regex filters': {str(e)}", err=True)
            ctx.exit(1)

    collections = _get_json_response_from_signed_request_paging(ctx, "collections", "Collections")
    if collections:
        collections = collections.get('collections')
    if collections:
        if filter:
            collections = [collection for collection in collections if re.search(filter, collection.get('id', ""))]
        if all:
            outfile.write(json.dumps({'collections': collections}, indent=indent))
            outfile.write("\n")
        else:
            for collection in collections:
                outfile.write(f"{collection['id']}\n")
                if title and 'title' in collection:
                    outfile.write(f"Title: {collection['title']}\n")
                if description and 'description' in collection:
                    outfile.write(f"Description: {collection['description']}\n")
                if title or description:
                    outfile.write("\n")

@item.command("search")
@click.option("-c", "--collection", "collections", type=str, show_default=False,default=None, help="Filter by collection ID(s). Separate multiple IDs with ','")
@click.option("-b", "--bbox", nargs=4, type=float, help="Filter items by bounding box (xmin, ymin, xmax, ymax).")
@click.option("-d", "--datetime", type=str, help="Filter items by time range (e.g., 2020-01-01/2020-12-31).")
@click.option("-f", "--filter", "filter_expr", type=str, help="CQL2-text filter expression.")
@click.option("-l", "--limit", type=int, help="Limit the number of items returned in a single request.")
@click.option("-m", "--max", type=int, help="Limit the total number of items returned.")
@click.option("--all", default=False, is_flag=True, help="Output the full JSON for each item.")
@click.option("-p", "--pretty", default=False, is_flag=True, help="Pretty-print JSON output.")
@click.option("-o", "--outfile", type=click.File('w', encoding='utf8'), default=click.get_text_stream('stdout'), help="Write output to a file instead of stdout.")
@click.option("-a", "--assets", "assetfilter", default=None, type=str, show_default=False, help="Only print specified assets, multiple assets are separated by ','")
@click.option("-r", "--href-only", default=False, is_flag=True, show_default=False, help="Only print asset hrefs")
@click.option("-s", "--strip-file", default=False, is_flag=True, show_default=False, help="Remove file prefix from asset hrefs")
@click.pass_context
def search_items(ctx: dict, collections: str, bbox, datetime, filter_expr, limit, max, all: bool, pretty: bool, outfile, assetfilter: str = None, href_only: bool = False, strip_file: bool = False):
    """Search STAC Items across collections.

    Search for items using various filters including spatial, temporal, and custom expressions.
    The search endpoint allows querying across multiple collections at once.

    Examples:
    - Search all items: `terrapi stac item search`
    - Filter by collection: `terrapi stac item search --collection landsat-c2-l2`
    - Filter by bbox: `terrapi stac item search --bbox -180 -90 180 90`
    - Filter by time: `terrapi stac item search --datetime "2020-01-01/2020-12-31"`
    - Use CQL2 filter: `terrapi stac item search --filter "eo:cloud_cover < 10"`
    """
    if href_only and all:
        handle_error(ctx, "Error: Options --all and --href-only cannot be used together.", 1)

    if assetfilter:
        assetfilter = assetfilter.split(",")
       
    # Build search parameters
    params = {}
    if collections:
        collections = collections.split(",") 
        params['collections'] = collections
    if max and not limit:
        limit = max
    if limit:
        params['limit'] = min(limit, max) if max else limit
    if datetime:
        params['datetime'] = datetime
    if bbox:
        validate_bbox_exit_error(bbox)
        params['bbox'] = list(bbox)
    if filter_expr:
        # Note: This assumes the STAC API supports CQL2-text
        params['filter'] = filter_expr
        #params['filter-lang'] = 'cql2-text'

    # Use the /search endpoint
    search_response = _get_json_response_from_signed_request(ctx, "search", "Item Search", method="GET", json=params)
    


    if search_response:
        items = search_response.get('features', [])
        indent = 2 if pretty else 0
        
        if items:
            new_items = []
            if max and len(items) > max:
                items = items[:max]
                
            for item in items:
                if not (href_only or all):
                    # Print minimal info: collection/id
                    collection = item.get('collection', 'unknown')
                    outfile.write(f"{collection}/{item.get('id')}\n")
                    continue
                    
                new_item, hrefs = _filterItemStripHref(item, href_only, strip_file, assetfilter)
                if href_only:
                    for href in hrefs:
                        outfile.write(f"{href}\n")
                    continue
                new_items.append(new_item)
                
            if all:
                outfile.write(json.dumps({
                    'features': new_items, 
                    "type": "FeatureCollection",
                    "numberMatched": search_response.get('numberMatched'),
                    "numberReturned": len(new_items)
                }, indent=indent) + "\n")

@item.command("list")
@click.argument("collection_id", type=str)
@click.option("-b", "--bbox", nargs=4, type=float, help="Filter items by bounding box (xmin, ymin, xmax, ymax).")
@click.option("-d", "--datetime", type=str, help="Filter items by time range (e.g., 2020-01-01/2020-12-31).")
@click.option("-l", "--limit", type=int, help="Limit the number of items returned in a single request.")
@click.option("-m", "--max", type=int, help="Limit the total number of items returned.")
@click.option("--all", default=False, is_flag=True, help="Output the full JSON for each item.")
@click.option("-p", "--pretty", default=False, is_flag=True, help="Pretty-print JSON output.")
@click.option("-o", "--outfile", type=click.File('w', encoding='utf8'), default=click.get_text_stream('stdout'), help="Write output to a file instead of stdout.")
@click.option("-a", "--assets", "assetfilter", default=None, type=str, show_default = False, help="Only print specified assets, multiple assets are separated by ',' ")
@click.option("-r", "--href-only", default=False, is_flag = True, show_default = False, help="Only print asset hrefs")
@click.option("-s", "--strip-file", default=False, is_flag = True, show_default = False, help="Remove file prefix from asset hrefs")
@click.pass_context
def list_item(ctx: dict, collection_id: str, bbox, datetime, limit, max, all: bool, pretty: bool, outfile,assetfilter:str=None,href_only:bool=False, strip_file:bool=False):
    """List STAC Items in a Collection.

    Retrieve and display metadata for items in a specific collection. You can filter items by spatial and temporal properties, or output the full JSON.

    Examples:
    - List all items: `terrapi stac item list <collection_id>`
    - Filter items by bounding box: `terrapi stac item list <collection_id> --bbox -180 -90 180 90`
    - Filter items by time range: `terrapi stac item list <collection_id> --datetime "2020-01-01/2020-12-31"`
    """
    if href_only and all:
       handle_error(ctx,"Error: Options --all and --href-only cannot be used together.", 1)

    params = {}
    if max and not limit:
        limit = max
    if limit:
        params['limit'] = min(limit, max) if max else limit
    if datetime:
        params['datetime'] = datetime
    if bbox:
        validate_bbox_exit_error(bbox)
        params['bbox'] = ','.join(map(str, bbox))

    path = f"collections/{collection_id}/items"
    feature_collection = _get_json_response_from_signed_request(ctx, path, f"Items in Collection {collection_id}", params=params)
    if feature_collection:
        items = feature_collection.get('features', [])
        indent = 2 if pretty else 0
        if items:
            new_items = []
            if max and len(items) > max:
                items = items[:max]
            for item in items:
                if not (href_only or all):
                    outfile.write(f"{item.get('id')}\n")
                    continue
                new_item, hrefs = _filterItemStripHref(item, href_only, strip_file, assetfilter)
                if href_only:
                    for href in hrefs:
                        outfile.write(f"{href}\n")
                    continue
                new_items.append(new_item)
            if all:
                outfile.write(json.dumps({'features': new_items, "type": "FeatureCollection"}, indent=indent) + "\n")


@item.command("queryables")
@click.argument("collection_id", type=str)
@click.option("-p", "--pretty", default=False, is_flag=True, help="Pretty-print JSON output.")
@click.option("-o", "--outfile", type=click.File('w', encoding='utf8'), default=click.get_text_stream('stdout'), help="Write output to a file instead of stdout.")
@click.pass_context
def get_queryables(ctx: dict, collection_id: str, pretty: bool, outfile):
    """Get queryable attributes for items in a collection.

    Retrieves the schema of queryable attributes that can be used for filtering items
    in the specified collection using CQL2 expressions.

    Examples:
    - Get queryables: `terrapi stac item queryables <collection_id>`
    - Pretty print: `terrapi stac item queryables <collection_id> --pretty`
    """
    path = f"collections/{collection_id}/queryables"
    queryables = _get_json_response_from_signed_request(ctx, path, f"Queryables for Collection {collection_id}")
    
    if queryables:
        indent = 2 if pretty else 0
        outfile.write(json.dumps(queryables, indent=indent) + "\n")

@collection.command()
@click.argument("collection_id")
@click.confirmation_option(help='Confirm deletion.', prompt='Are you sure you want to delete the Collection?')
@click.pass_context
def delete(ctx: dict, collection_id:str):
    """ Delete a Collection defined by its ID
    
    This will permanently delete the specified collection with all its Items from the private STAC Catalogue. 
    """
    if ctx.obj['noAuth']:
       handle_error("ERROR! Delete is only possible for private stac API. Exiting", 3)
    response=_get_json_response_from_signed_request(ctx,f"collections/{collection_id}" , f"deletion of {collection_id}", method="DELETE")
    if not response:
        handle_error(ctx,f"Failed to delete Collection {collection_id}",1)
    returned_id=response.get('deleted collection',None)
    if returned_id == id:
        click.echo(f"Deleted Collection {collection_id}")


@item.command("delete")
@click.argument("collection_id")
@click.argument("item_id")
@click.confirmation_option(help='Confirm deletion.', prompt='Are you sure you want to delete the Item?')
@click.pass_context
def delete_item(ctx: dict, collection_id:str, item_id:str):
    """ Delete an Item from Collection
    
    
    This will permanently delete the specified Item from the STAC Catalogue. 
    """
    if ctx.obj['noAuth']:
       handle_error(ctx, "ERROR! Delete is only possible for private stac API. Exiting")
    response=_get_json_response_from_signed_request(ctx,f"collections/{collection_id}/items/{item_id}" , f"deletion of {collection_id}", method="DELETE")
    if not response:
        handle_error(ctx,f"Failed to delete Item {item_id} from {collection_id}")
    else :
        returned_id=response.get('deleted item',None)
        if returned_id == item_id:
            click.echo(f"Deleted Item {item_id}")




 

@collection.command()
@click.option("--id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.option("-u", "--update",default=False, is_flag = True, show_default = False,help='Update Collection if it allready exists')
@click.option("-q", "--quiet",default=False, is_flag = True, show_default = False,help='Do not print response')
@click.pass_context
def create(ctx: dict, id: str = None, json_str: str = None, inputfile:TextIO = None,update: bool = False ,quiet: bool =False )->None:
    """Create a new STAC Collection 
    
    The Collection json can be specfied either from stdin, from a file or as a parameter. \n
    The Stac Server returns updated version of the Collection 

    """
    if ctx.obj['noAuth']:
      handle_error(ctx,"ERROR! Create is only possible for private stac API. Exiting")
    collection=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements 
    if id:
        collection['id']=id
    else:
        id=collection.get('id')
    alt_method=None if not update else "PUT"
    response=_get_json_response_from_signed_request(ctx,"collections" , f"Create Collection {id}", method="POST",alt_method=alt_method,alt_code=409, json=collection)
    if response and not quiet:
        click.echo(json.dumps(response))

@item.command("create")
@click.argument("collection_id", type=str)
@click.option("--id","item_id",default=None,type=str, help="ID of the Item. If specified will overwrite the ID in the Item JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.option("-u", "--update",default=False, is_flag = True, show_default = False,help='Update Item if it allready exists')
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.option("-q", "--quiet",default=False, is_flag = True, show_default = False,help='Do not print response')
@click.pass_context
def create_item(ctx: dict,collection_id:str,item_id: str = None, json_str: str = None, inputfile:TextIO = None,update: bool = False, pretty:bool =False, quiet: bool =False  )->None:
    """Create new Item(s) in specified Collection 
    
    The Item  json can be specfied either from stdin, from a file or as a parameter. \n
    It can either be the json of a single Item, or to batch create a FeatureCollection with an array of items as features\n
    In case of the list of items make sure they do not exist in collection as update path is not possible in this use case. \n
    In case of singe Item, the server formated new Item is returned unless quiet flag is passed. 
    In case of a FeatureCollections no Items are returned by default. \n 

    """
    if ctx.obj['noAuth']:
       handle_error(ctx,"ERROR! Create is only possible for private stac API. Exiting")
    item=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements
    #distinquish between single item and 
    if item.get("type","") == "Feature":
        if item_id:
            item['id']=item_id
        else:
            item_id=item.get('id')
        if ctx.obj['DEBUG']:
            click.echo(f"Setting Collection ID to {collection_id}")
        item.update({"collection":collection_id})
    else:
        items=item.get("features",None)
        #not possible for featurecollection
        if update: 
            handle_error(ctx, "Error: Update is not possible when providing a FeatureCollection with multiple items. Please create items individually if fallback to update is needed", 5)  
        update=False
        if items:
            if item_id:
                click.echo(f"item_id is {item_id} and type {item_id}")
                item_id=item_id.split(",")
                if (len(item_id)!=len(items)):
                    handle_error(ctx, f"Error updating ItemIds. Received a FeatureCollection with {len(items)}, but only {len(item_id)} after splitting provided ID List={item_id} at ',' Please recheck!",7)
                    
            idpointer=0
            for sitem in items:
                sitem.update({"collection":collection_id})
                if item_id:
                    sitem.update({"id":item_id[idpointer]})
                    idpointer = idpointer + 1
        else:
            handle_error(ctx, f"Error Expected a Feature Collection but did not find the features list. \n JSON was: {item}",8)
        item_id="Feature Collection"
    if(ctx.obj["DEBUG"]):
        click.echo(f"Modified JSON to upload is: \n {json.dumps(item)}")
    alt_method=None if not update else "PUT"
    alt_code=409
    response=_get_json_response_from_signed_request(ctx=ctx, stac_path=f"collections/{collection_id}/items" , error_desc=f"Create Item {item_id} in Collection {collection_id}", method="POST",alt_method=alt_method,alt_code=alt_code, json=item)
    if response and not quiet:
        ind=2 if pretty else 0
        click.echo(json.dumps(response,indent=ind))


@collection.command()
@click.option("--id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.pass_context
def update(ctx: dict,id: str = None, json_str: str = None, inputfile:TextIO = None, pretty:bool =False):
    """Update an existing Collection
    
    The Collection json can be specfied either from stdin, from a file or as a parameter. 
    """
    if ctx.obj['noAuth']:
       click.echo("ERROR! Update is only possible for private stac API. Exiting", err=True)
       exit(3)
    collection=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements 
    if id:
        collection['id']=id
    else:
        id=collection.get('id')

    response=_get_json_response_from_signed_request(ctx,f"collections/{id}" , f"Update Collection {id}", method="PUT", json=collection)
    if response:
        indent=2 if pretty else 0 
        click.echo(json.dumps(response,indent=indent))
      
@item.command("update")
@click.argument("collection_id", type=str)
@click.option("--id","item_id",default=None,type=str, help="ID of the Item. If specified will overwrite the ID in the Item JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.pass_context
def update_item(ctx: dict,collection_id:str,item_id: str = None, json_str: str = None, inputfile:TextIO = None, pretty:bool =False):
    """Update an existing Item 
    
    The Item  json can be specfied either from stdin, from a file or as a parameter.
    """
    if ctx.obj['noAuth']:
       handle_error(ctx,"ERROR! Update is only possible for private stac API. Exiting", exit_code=3)

    item=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements 
    if item_id:
        item['id']=item_id
    else:
        item_id=item.get('id')
    if collection_id is None or item_id is None:
        click.echo(f"Error None Value in Collection Id ({collection_id}) or Item ID ({item_id})",err=True)
        exit(6)
    item.update({"collection":collection_id})
    response=_get_json_response_from_signed_request(ctx,f"collections/{collection_id}/items/{item_id}" , f"Updating Item {item_id} in Collection {collection_id}", method="PUT", json=item)
    if response: 
        indent=2 if pretty else 0 
        click.echo(json.dumps(response,indent=indent))
      
@item.command("validate")
@click.option("-c","collection_id", default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Item JSON")
@click.option("-i","item_id", default=None,type=str, help="ID of the Item. If specified will overwrite the ID in the Item JSON")
@click.option("-f", "--file", "inputfile", type=click.File('r', encoding='utf8'), help='Read Item JSON from File. Specify - to read from pipe') 
@click.option("-j", "--json", "json_str", type=str, help="Provide item as JSON String")
@click.pass_context
def validate_item(ctx: dict, collection_id: str, item_id: str, inputfile: TextIO = None, json_str: str = None):
    """Validate a STAC Item.

    This command validates the structure and content of a STAC Item against the STAC specification.
    The `validate_stac_item` function ensures that the provided item adheres to the required schema and standards.
    """

    success, errors = validate_stac_item(item)
    if not success:
        click.echo("Validation failed. The item is not valid.", err=True)
        if errors:
            click.echo("Validation Errors:", err=True)
            for error in errors:
                click.echo(f"- {error}", err=True)
        ctx.exit(1)
    click.echo("Congratulations! The item is valid.")
    if item_id:
        item['id']=item_id
    if collection_id:
        item['collection']=collection_id
    success= validate_stac_item(item)
    if not success:
        click.echo("Validation failed. The item is not valid.", err=True)
        ctx.exit(1)
    click.echo("Congratulations Item is valid.")
    
@collection.command()
@click.argument("collection_id", type=str)
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.option("-o", "--outfile","outfile",type=click.File('w', encoding='utf8'), help='Output file.', default=click.get_text_stream('stdout'))
@click.pass_context
def get(ctx: dict,collection_id:str,outfile:TextIO, pretty:bool =False):
    """ Get STAC Metadata for a single Collection 
    
    It requires the Collection ID as an Argument
    """
    path = f"collections/{collection_id}"
    collection = _get_json_response_from_signed_request(ctx, path, f"Collection {collection_id}")
    if collection:
        indent = 2 if pretty else 0
        outfile.write(json.dumps(collection, indent=indent) + "\n")


@item.command("get")
@click.argument("collection_id", type=str)
@click.argument("item_id", type=str)
@click.option("-p", "--pretty", default=False, is_flag=True, help="Pretty-print JSON output.")
@click.option("-o", "--outfile", type=click.File('w', encoding='utf8'), default=click.get_text_stream('stdout'), help="Write output to a file instead of stdout.")
@click.option("-a", "--assets", "assetfilter", default=None, type=str, help="Only print specified assets, multiple assets are separated by ','.")
@click.option("-r", "--href-only", default=False, is_flag=True, help="Only print asset hrefs.")
@click.option("-s", "--strip-file", default=False, is_flag=True, help="Remove file prefix from asset hrefs.")
@click.pass_context
def get_item(ctx: dict, collection_id: str, item_id: str, outfile, pretty: bool, assetfilter: str, href_only: bool, strip_file: bool):
    """Retrieve metadata for a single STAC item.

    This command fetches metadata for a specific item in a collection. Use the `--href-only` option to print only asset hrefs.

    Examples:
    - Get item metadata: `terrapi stac item get <collection_id> <item_id>`
    - Get asset hrefs: `terrapi stac item get <collection_id> <item_id> --href-only`
    """
    path = f"collections/{collection_id}/items/{item_id}"
    item = _get_json_response_from_signed_request(ctx, path, f"Item {item_id} from Collection {collection_id}")
    if item:
        indent = 2 if pretty else 0
        if assetfilter:
            assetfilter = assetfilter.split(",")
        if assetfilter or href_only or strip_file:
            item, hrefs = _filterItemStripHref(item, href_only, strip_file, assetfilter)
        if href_only:
            for href in hrefs:
                outfile.write(href + "\n")
        else:
            outfile.write(json.dumps(item, indent=indent) + "\n")


@collection.command()
@click.pass_context
def prefix(ctx:dict):
    """ List all acceptable read/writable prefixes for specific user
    
    The information about the prefixes is extracted from the current refresh token. 
    Therefore if a new dss invite was accepted lately it is recommended to force the update of the token via the login function.   
    """
    tokens = _get_auth_refresh_tokens(ctx)
    if tokens is None:
        exit(1)
    rw_prefix,ro_prefix = _get_valid_prefixes(tokens.access_token)
    if rw_prefix:
        click.echo("Writable Collection prefixes:")
        for p in rw_prefix:
            click.echo(p)
    if ro_prefix:
        click.echo("Readonly Collection prefixes:")
        for p in ro_prefix:
            click.echo(p)



stac.add_command(collection)
stac.add_command(item)
stac.add_command(login)
stac.add_command(auth)

if __name__ == '__main__':
    stac()