import click
import json
import ast
import re
import jwt
import traceback
from typing import Tuple, TextIO
import requests


from ..settings import  TERRABYTE_PUBLIC_API_URL



from ..adapter import wrap_request
from .shared_cli import login, auth, _get_auth_refresh_tokens


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

def _get_json_response_from_signed_request(ctx:dict,stac_path:str, error_desc:str, method="GET",alt_method: str = None,alt_code:int =-1, **kwargs)->dict:
    url=f"{ctx.obj['privateAPIUrl']}/{stac_path}" 
    if ctx.obj['noAuth']: 
        url=f"{ctx.obj['publicStacUrl']}/{stac_path}"
    return(_get_json_response_from_signed_url(ctx,url, error_desc, method,alt_method,alt_code, **kwargs))



def _get_json_response_from_signed_url(ctx:dict,url:str, error_desc:str, method="GET",alt_method: str = None,alt_code:int =-1, noAuth: bool=False,**kwargs)->dict:
    debugCli =ctx.obj['DEBUG']
    if debugCli:
        print(f" Requesting {error_desc} from {url} using {method}")
    try:   
        if ctx.obj['noAuth']: 
            r = requests.request(url=url, method=method, **kwargs)
        else:  
            r=wrap_request(requests.session(),url=url,client_id=ctx.obj['ClientId'],method=method,**kwargs)      
        #check if request was successful 
        # see https://github.com/stac-utils/stac-fastapi/blob/add05de82f745a717b674ada796db0e9f7153e27/stac_fastapi/api/stac_fastapi/api/errors.py#L23
        # https://stac.terrabyte.lrz.de/public/api/api.html#/
        #fastAPI errors:
        if alt_method and r.status_code == alt_code :
            if debugCli:
                click.echo(f"Request to {url} using {method} failed with error Code 409. Retrying with  {alt_method}",err=True)
            if ctx.obj['noAuth']: 
                r2= requests.request(url=url, method=alt_method, **kwargs)
            else:  
                r2=wrap_request(requests.session(),url=url,client_id=ctx.obj['ClientId'],method=alt_method,**kwargs)
            #if alt request was succesful switch to it
            if 200<=r2.status_code<=299:
                r=r2
        json_stac=r.json()
        message=json_stac.get('message', None)
        match r.status_code:
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
        click.echo(f"Requesting {error_desc} from URL {url} failed")
        if debugCli:
            click.echo("Error reported was:")
            click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            traceback.print_exc()
        return None

def _readJson_from_file_or_str(json_str:str = None, inputfile:TextIO = None, debugCli=False) ->dict:
    if (inputfile is None and json_str is None) or (inputfile and json_str):
        click.echo("Error. Either JSON String or JSON File have to be specified. Exiting",err=True)
        exit(4)
        
    if inputfile: 
        try: 
            json_dict=json.loads(inputfile.read())
        except Exception as e:
           #fallback to also try reading it via ast?
           click.echo(f"Failed to import valid JSON from File {inputfile.name}. Exiting",err=True)
           if debugCli:
             click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
             traceback.print_exc()  
           exit(5)
        return json_dict
    if json_str: 
        try:
            json_dict=json.loads(json_str)
            return json_dict
        except Exception as e:
            try:
                if debugCli: 
                    click.echo("json.loads failed. Falling back to ask convert", err=True)
                    click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
                    traceback.print_exc()  
                json_dict = ast.literal_eval(json_str)
            except Exception as e:
                click.echo(f"Failed to convert the String {json_str} to valid JSON. Exiting",err=True)
                if debugCli:
                    click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
                    traceback.print_exc()  
                exit(5)
    #should never be reached
    return {}


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


@click.group()
@click.option("-p", "--public",default=False, is_flag = True, show_default = False, help="Switch to public API")
@click.option("--privateURL","private_url",type=str,   show_default = False, default = None, help="overwrite private Stac URL.  Warning expert OPTION! ")
@click.option("--publicURL","public_url",type=str,   show_default = False, default = None, help="overwrite public Stac URL.  Warning expert OPTION! ")
@click.option("--clientID", "client_id",type=str, default = None, help="overwrite clientID.  Warning expert OPTION!", hidden=True)
#@click.option("--scope", "scope",type=str,default = None, help="add scope, seperate multiple with ','", hidden=True)
@click.pass_context
def stac(ctx:dict, public: bool = False ,private_url:str = None, public_url:str = None, client_id:str=None, scope:str=None):
    """Command Line for terrabyte private STAC API
    The private Stac Api allows you to create/update your own private or shared (between all users of a dss container) STAC Collections and Items
    To mark a collection as private prepend the name of the collection with your LRZ username, e.g., something like "di99abc.Sentinel2Classification"
    To mark a collection as shared prepend its name with DSS Container ID  like "pn56su-dss-0020" 
    All write/readable prefixes can be obtained from the sub command prefix
    """
    if private_url:
        ctx.obj['privateAPIUrl']=private_url
        if ctx.obj['DEBUG']: 
            click.echo(f"Api URl is now {private_url}")

    if public_url:
        ctx.obj['publicStacUrl']=public_url
        public=True
        if ctx.obj['DEBUG']: 
            click.echo(f"Api URl is now {public_url}")
    else:
        ctx.obj['publicStacUrl']=TERRABYTE_PUBLIC_API_URL
    
    ctx.obj['noAuth']=public
    if public and ctx.obj['DEBUG']:
        click.echo("Switching to public STAC API. Update/modify not possible")
        click.echo(f"Api URl is now {ctx.obj['publicStacUrl']}")
    
    if client_id:
        if ctx.obj['DEBUG']: 
            click.echo(f"Client ID is now {client_id}")
        ctx.obj['ClientId']=client_id
        
    if scope:
        oidScopes=scope.split(",")
        if ctx.obj['DEBUG']: 
            click.echo(f"Adding Scope(s): {oidScopes}")
        ctx.obj['oidScopes']=[scope]

        
    

#define subcommands
@click.group()
@click.pass_context
def collection(ctx: dict):
    """ Interact with STAC Collection(s)"""
    #print("in Collection")
    pass

@click.group()
@click.pass_context
def item(ctx: dict):
    """ Interact with Stac Item(s)"""
    pass



@collection.command()
@click.option("-f","--filter",type=str, default="", help="Filter Collection ID with regex")
@click.option("-t", "--title",default=False, is_flag = True, show_default = False, help="Add Title to output")
@click.option("-d", "--description",default=False, is_flag = True, show_default = False, help="Add Description to output")
@click.option("-a", "--all", default=False, is_flag = True, show_default = False, help="Write whole Collection JSOn to output")
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="Indent Json Printing")
@click.option("-o", "--outfile","outfile",type=click.File('w', encoding='utf8'), help='Write Collections to this file instead of stdout', default=click.get_text_stream('stdout'))
@click.pass_context
def list(ctx: dict,outfile:TextIO,filter: str ="", title: bool = False, description: bool = False,all:bool=False, pretty:bool=False):
    """ List STAC Collections
    
    Collections can be filtered by regular Expressions and written to File """
    indent=0
    if pretty:
        indent=2
    collections=_get_json_response_from_signed_request_paging(ctx,"collections", "Collections")
    if collections:
        collections=collections.get('collections')
    if collections:
        if filter != "":
            collections=[collection for collection in collections if re.search(filter, collection.get('id',""))]
        if all:
            outfile.write(json.dumps({'collections':collections},indent=indent))
            outfile.write("\n")
        else:          
            for collection in collections:
                outfile.write(f"{collection['id']}\n")
                if title and 'title' in collection:
                    outfile.write(f"title= '{collection['title']}'")
                if description and 'description' in collection:
                    outfile.write(f"description= '{collection['description']}'\n")
                    outfile.write("\n")
    
@item.command("list")
#@click.option("-f","--filter", type=str, default="", help="Filter Expression as jw")
@click.option( "--all", default=False, is_flag = True, show_default = False, help="Print whole STAC Item")
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="Indent Item Printing")
@click.option("-b", "--bbox",  nargs=4, default=None, type=float, help="Bounding Box for results: xmax, ymax, xmin, ymin Lon/Lat Coordinates")
@click.option("-d", "--datetime", default=None, type=str, help="Time Range of results. E.g 2018-02-12T00:00:00Z/2018-03-18T12:31:12Z")
@click.option("-l","--limit", default=None, type=int, help="Maximum Number of Items to request from API in one call")
@click.option("-m","--max", default=None, type=int, help="Maximum Number of Items to receive in total")
#@click.option("-d", "--description",default=False, is_flag = True, show_default = False, help="Print Description to output")
@click.option("-a","--assets", "assetfilter", default=None, type=str, show_default = False, help="Only print specified assets, multiple assets are separated by ',' ")
@click.option("-h", "--href-only", default=False, is_flag = True, show_default = False, help="Only print asset hrefs")
@click.option("-s","--strip-file", default=False, is_flag = True, show_default = False, help="Remove file prefix from asset hrefs")
@click.option("-o", "--outfile","outfile",type=click.File('w', encoding='utf8'), help='Write Results to this file', default=click.get_text_stream('stdout'))
@click.argument("collection_id", type=str)
@click.pass_context
def list_item(ctx: dict,collection_id:str,outfile:TextIO, all: bool = False, pretty: bool = False,bbox= None,datetime=None, limit=None, max=None,assetfilter:str=None,href_only:bool=False, strip_file:bool=False):
    """ List STAC Items in a specific Collection 
    
    The items can be filtered by time and space. It is also possible to specify spefic assets as well as only printing the path to the assets. 
    """
    if href_only and all:
        click.echo("Warning options --all and --href-only make no sense together! Decide what you want! Everything or only the file links! Then come back and try again",err=True, color="Red")
        exit(1)
    kwargs={}
    params={}
    if max and not limit:
        limit=max
    if limit:
        if max:
            limit=min(limit,max)
        params.update({'limit':limit})
    if datetime:
        params.update({'datetime':datetime})
    if bbox:
        params.update({'bbox':','.join(str(b) for b in bbox) })
    if params:
        kwargs.update({'params': params})
    if assetfilter:
        assetfilter=assetfilter.split(",")
    
    
    featureCollection=_get_json_response_from_signed_request_paging(ctx,f"collections/{collection_id}/items", f"Items in Collection {collection_id}",maxElements=max, **kwargs)
   #['collections']
   # click.echo(json.dumps(featureCollection['features'],indent=2))
    if featureCollection:
        items=featureCollection.get('features')
        indent=2 if pretty else 0
        if items:
            new_items=[]
            if max and len(items)> max:
                items =items[:max]
            for item in items:
                if not (href_only or all):
                    outfile.write(f"{item.get('id')}\n")
                    continue
                newitem,hrefs=_filterItemStripHref(item,href_only, strip_file, assetfilter)
                if href_only:
                    for href in hrefs:
                        outfile.write(href)
                        outfile.write("\n")
                    continue
                new_items.append(newitem)
            if all:
                outfile.write(json.dumps({'features':new_items},indent=indent))
                outfile.write("\n")



#@collection.command()
#def search():



@collection.command()
@click.argument("collection_id")
@click.confirmation_option(help='Confirm deletion.', prompt='Are you sure you want to delete the Collection?')
@click.pass_context
def delete(ctx: dict, collection_id:str):
    """ Delete a Collection defined by its ID
    
    This will permanently delete the specified collection with all its Items from the private STAC Catalogue. 
    """
    if ctx.obj['noAuth']:
       click.echo("ERROR! Delete is only possible for private stac API. Exiting", err=True)
       exit(3)
    response=_get_json_response_from_signed_request(ctx,f"collections/{collection_id}" , f"deletion of {collection_id}", method="DELETE")
    if not response:
        click.echo(f"Failed to delete Collection {collection_id}")
    else :
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
    
    
    This will permanently delete the specified Item from the STAC Catalogue
    """
    if ctx.obj['noAuth']:
       click.echo("ERROR! Delete is only possible for private stac API. Exiting", err=True)
       exit(3)
    response=_get_json_response_from_signed_request(ctx,f"collections/{collection_id}/items/{item_id}" , f"deletion of {collection_id}", method="DELETE")
    if not response:
        click.echo(f"Failed to delete Item {item_id} from {collection_id}")
    else :
        returned_id=response.get('deleted item',None)
        if returned_id == item_id:
            click.echo(f"Deleted Item {item_id}")




 

@collection.command()
@click.option("--id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.option("-u", "--update",default=False, is_flag = True, show_default = False,help='Update Collection if it allready exists')
@click.pass_context
def create(ctx: dict, id: str = None, json_str: str = None, inputfile:TextIO = None,update: bool = False )->None:
    """Create a new STAC Collection 
    
    The Collection json can be specfied either from stdin, from a file or as string parameter. 
    """
    if ctx.obj['noAuth']:
       click.echo("ERROR! Create is only possible for private stac API. Exiting", err=True)
       exit(3)
    collection=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements 
    if id:
        collection['id']=id
    else:
        id=collection.get('id')
    alt_method=None

    if update:
        alt_method = "PUT"
    response=_get_json_response_from_signed_request(ctx,"collections" , f"Create Collection {id}", method="POST",alt_method=alt_method,alt_code=409, json=collection)
    if response:
        click.echo(json.dumps(response))

@item.command("create")
@click.argument("collection_id", type=str)
@click.option("--id","item_id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.option("-u", "--update",default=False, is_flag = True, show_default = False,help='Update Collection if it allready exists')
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.pass_context
def create_item(ctx: dict,collection_id:str,item_id: str = None, json_str: str = None, inputfile:TextIO = None,update: bool = False, pretty:bool =False )->None:
    """Create a new Item in specified Collection 
    
    The Item  json can be specfied either from stdin, from a file or as string parameter. 
    """
    if ctx.obj['noAuth']:
       click.echo("ERROR! Create is only possible for private stac API. Exiting", err=True)
       exit(3)
    item=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements 
    if item_id:
        item['id']=item_id
    else:
        item_id=item.get('id')
    alt_method=None
    alt_code=409
    if update:
        alt_method = "PUT"
    response=_get_json_response_from_signed_request(ctx,f"collections/{collection_id}/items" , f"Create Item {item_id} in Collection {collection_id}", method="POST",alt_method=alt_method,alt_code=alt_code, json=item)
    if response:
        indent=2 if pretty else 0
        click.echo(json.dumps(response,indent))


@collection.command()
@click.option("--id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.pass_context
def update(ctx: dict,id: str = None, json_str: str = None, inputfile:TextIO = None, pretty:bool =False):
    """Update an existing Collection
    
    The Collection json can be specfied either from stdin, from a file or as string parameter. 
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
    
    The Item  json can be specfied either from stdin, from a file or as string parameter.
    """
    if ctx.obj['noAuth']:
       click.echo("ERROR! Update is only possible for private stac API. Exiting", err=True)
       exit(3)
    item=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements 
    if item_id:
        item['id']=item_id
    else:
        item_id=item.get('id')
    if collection_id is None or item_id is None:
        click.echo(f"Error None Value in Collection Id ({collection_id}) or Item ID ({item_id})",err=True)
        exit(6)
    response=_get_json_response_from_signed_request(f"collections/{collection_id}/items/{item_id}" , f"Updating Item {item_id} in Collection {collection_id}", method="PUT", json=item)
    if response: 
        indent=2 if pretty else 0 
        click.echo(json.dumps(response,indent=indent))
      




@collection.command()
@click.argument("collection_id", type=str)
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.option("-o", "--outfile","outfile",type=click.File('w', encoding='utf8'), help='Output file.', default=click.get_text_stream('stdout'))
@click.pass_context
def get(ctx: dict,collection_id:str,outfile:TextIO, pretty:bool =False):
    """ Get STAC Metadata for a single Collection 
    
    It requires the Collection ID as an Argument
    """
    collection=_get_json_response_from_signed_request(ctx,f"collections/{collection_id}" , f"Collection {collection_id}", method="GET")
    if collection:
        indent=2 if pretty else 0 
        outfile.write(json.dumps(collection,indent=indent))
        outfile.write("\n")



@item.command("get")
@click.argument("collection_id", type=str)
@click.argument("item_id",type=str)
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.option("-o", "--outfile","outfile",type=click.File('w', encoding='utf8'), help='Output file.', default=click.get_text_stream('stdout'))
@click.option("-a","--assets", "assetfilter", default=None, type=str, show_default = False, help="Only Print specified assets, assets are separated by ',' ")
@click.option("-h", "--href-only", default=False, is_flag = True, show_default = False, help="Only Print asset hrefs")
@click.option("-s","--strip-file", default=False, is_flag = True, show_default = False, help="Remove file prefix from asset hrefs")
@click.pass_context
def get_item(ctx: dict, collection_id:str, item_id:str, outfile:TextIO, pretty:bool =False,assetfilter:str=None,href_only:bool=False, strip_file:bool=False):
    """ Get STAC Metadata for a single Item 
    It requires the Collection ID and Item ID"""
    item=_get_json_response_from_signed_request(ctx,f"collections/{collection_id}/items/{item_id}" , f"Item {item_id} from Collection {collection_id}", method="GET")
    if item:
        indent=2 if pretty else 0 
        if assetfilter:
            assetfilter=assetfilter.split(",")
        if assetfilter or href_only or strip_file:
            item,hrefs=_filterItemStripHref(item,href_only,strip_file,assetfilter)
        if href_only:
            for href in hrefs:
                 outfile.write(href)
                 outfile.write("\n")
        else:
            outfile.write(json.dumps(item,indent=indent))
            outfile.write("\n")






@collection.command()
@click.pass_context
def prefix(ctx:dict):
    """ List all allowed read/writable prefixes for current user"""
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