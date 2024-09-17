import click
import json
import ast
import re
import jwt
import traceback
#from typing import Optional, List
import requests


from .settings import  TERRABYTE_PRIVATE_API_URL, TERRABYTE_CLIENT_ID, TERRABYTE_PUBLIC_API_URL

from .auth.config import RefreshTokenStore

from .adapter import wrap_request
from .shared_cli import login, auth, _get_auth_refresh_tokens


def _get_next_url(links)->str|None:
    for link in links:
        if link['rel']=='next':
            return link
    return None

def _get_json_response_from_signed_request_paging(ctx:dict,stac_path:str, error_desc:str, method="GET",alt_method: str = None,alt_code:int =-1, **kwargs)->dict:
    json_stac=_get_json_response_from_signed_request(stac_path, error_desc, method,alt_method,alt_code, **kwargs)
    if(json_stac.get("type")=="FeatureCollection"):
        nexUrl=_get_next_url(json_stac.get('links'))
        while nexUrl:
            extra_stac=_get_json_response_from_signed_url(ctx,nexUrl, error_desc, method,alt_method,alt_code, **kwargs)
            nexUrl=_get_next_url(extra_stac.get('links'))
            json_stac['features'].extent(extra_stac.get('features', None))
            json_stac['context']['limit']+=extra_stac['context']['limit']
        #remove next ling as we iterated over next links to download all items
        json_stac['links']=[link for link in json_stac['links'] if link['rel']!='next']
    return json_stac

def _get_json_response_from_signed_request(ctx:dict,stac_path:str, error_desc:str, method="GET",alt_method: str = None,alt_code:int =-1, **kwargs)->dict:
    url=f"{ctx.obj['privateStacUrl']}/{stac_path}" 
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

def _readJson_from_file_or_str(json_str:str = None, inputfile = None, debugCli=False) ->dict:
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
@click.option("--clientID", "client_id",type=str, default = None, help="overwrite clientID", hidden=True)
@click.option("--scope", "scope",type=str,default = None, help="add scope, seperate multiple with ','", hidden=True)
@click.pass_context
def stac(ctx:dict, public: bool = False ,private_url:str = None, public_url:str = None, client_id:str=None, scope:str=None):
    """Command Line for terrabyte private STAC API"""
    if private_url:
        ctx.obj['privateStacUrl']=private_url
        if ctx.obj['DEBUG']: 
            click.echo(f"Api URl is now {private_url}")
    else:
        ctx.obj['privateStacUrl']=TERRABYTE_PRIVATE_API_URL

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
    else:
        ctx.obj['ClientId']= TERRABYTE_CLIENT_ID
    if scope:
        oidScopes=scope.split(",")
        if ctx.obj['DEBUG']: 
            click.echo(f"Adding Scope(s): {oidScopes}")
        ctx.obj['oidScopes']=[scope]
    else:
        ctx.obj['oidScopes']=None
    ctx.obj['tokenStore']=RefreshTokenStore()

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
@click.pass_context
def list(ctx: dict,filter: str ="", title: bool = False, description: bool = False):
    """ List Collections"""
     
    collections=_get_json_response_from_signed_request_paging("collections", "Collections")['collections']
        
    for collection in collections:
        if re.search(filter, collection['id']):
            click.echo(collection['id'])
            if title and 'title' in collection:
                click.echo(f"title= '{collection['title']}'")
            if description and 'description' in collection:
                click.echo(f"description= '{collection['description']}'")
                click.echo("")
    
@item.command("list")
@click.option("-f","--filter", type=str, default="", help="Filter Expression as jw")
@click.option("-a", "--all", default=False, is_flag = True, show_default = False, help="Print whole Stac Item")
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="Indent Item Printing")
@click.option("-b", "--bbox",  nargs=4, default=None, type=float, help="Bounding Box for results: xmax, ymax, xmin, ymin Lon/Lat Coordinates")
@click.option("-d", "--datetime", default=None, type=str, help="Time Range of results. E.g 2018-02-12T00:00:00Z/2018-03-18T12:31:12Z")
@click.option("-l","--limit", default=None, type=int, help="Maximum Number of Items to request from API in one call")
@click.option("-m","--max", default=None, type=int, help="Maximum Number of Items to receive in total")
@click.option("-d", "--description",default=False, is_flag = True, show_default = False, help="Print Description to output")
#@click.option("-d", "--description",default=False, is_flag = True, show_default = False, help="Add Description to output")
@click.argument("collection_id", type=str)
@click.pass_context
def list_item(ctx: dict,collection_id:str, filter: str ="", all: bool = False, pretty: bool = False,bbox= None,datetime=None, limit=None, max=None):
    """ List Items in Collection """
    kwargs={}
    params={}
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


    
    featureCollection=_get_json_response_from_signed_request_paging(f"collections/{collection_id}/items", f"Items in Collection {collection_id}",maxElements=max, **kwargs)
   #['collections']
   # click.echo(json.dumps(featureCollection['features'],indent=2))
    items=featureCollection.get('features')
    indent=0
    if pretty: 
        indent=2
    if items:
        for item in items:
            if re.search(filter, item['id']):
                if all: 
                    click.echo(json.dumps(item,indent=indent))
                else: 
                    click.echo(item['id'])




#@collection.command()
#def search():



@collection.command()
@click.argument("collection_id")
@click.confirmation_option(help='Confirm deletion.', prompt='Are you sure you want to delete the Collection?')
@click.pass_context
def delete(ctx: dict, collection_id:str):
    """ Delete a Collection defined by its ID"""
    if ctx.obj['noAuth']:
       click.echo("ERROR! Delete is only possible for private stac API. Exiting", err=True)
       exit(3)
    response=_get_json_response_from_signed_request(f"collections/{collection_id}" , f"deletion of {collection_id}", method="DELETE")
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
    """ Delete an Item from Collection"""
    if ctx.obj['noAuth']:
       click.echo("ERROR! Delete is only possible for private stac API. Exiting", err=True)
       exit(3)
    response=_get_json_response_from_signed_request(f"collections/{collection_id}/items/{item_id}" , f"deletion of {collection_id}", method="DELETE")
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
def create(ctx: dict, id: str = None, json_str: str = None, inputfile = None,update: bool = False ):
    """Create a Collection from either String or File"""
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
    alt_code=409
    if update:
        alt_method = "PUT"
    response=_get_json_response_from_signed_request("collections" , f"Create Collection {id}", method="POST",alt_method=alt_method,alt_code=alt_code, json=collection)
    click.echo(json.dumps(response))

@item.command("create")
@click.argument("collection_id", type=str)
@click.option("--id","item_id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.option("-u", "--update",default=False, is_flag = True, show_default = False,help='Update Collection if it allready exists')
@click.pass_context
def create_item(ctx: dict,collection_id:str,item_id: str = None, json_str: str = None, inputfile = None,update: bool = False ):
    """Create a new Item in Collection from either String or File"""
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
    response=_get_json_response_from_signed_request(f"collections/{collection_id}/items" , f"Create Item {item_id} in Collection {collection_id}", method="POST",alt_method=alt_method,alt_code=alt_code, json=item)
    if response: 
        click.echo(json.dumps(response))


@collection.command()
@click.option("--id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.pass_context
def update(ctx: dict,id: str = None, json_str: str = None, inputfile = None):
    """Update an existing Collection from either String or File"""
    if ctx.obj['noAuth']:
       click.echo("ERROR! Update is only possible for private stac API. Exiting", err=True)
       exit(3)
    collection=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements 
    if id:
        collection['id']=id
    else:
        id=collection.get('id')
    response=_get_json_response_from_signed_request("collections" , f"Update Collection {id}", method="PUT", json=collection)
    if response: 
        click.echo(json.dumps(response))
      
@item.command("update")
@click.argument("collection_id", type=str)
@click.option("--id","item_id",default=None,type=str, help="ID of the Item. If specified will overwrite the ID in the Item JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
@click.pass_context
def update_item(ctx: dict,collection_id:str,item_id: str = None, json_str: str = None, inputfile = None):
    """Update an existing Item from either String or File"""
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
        click.echo(json.dumps(response))
      




@collection.command()
@click.argument("collection_id", type=str)
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.option("-f", "--file","outfile",type=click.File('w', encoding='utf8'), help='Output file.', default=click.get_text_stream('stdout'))
@click.pass_context
def get(ctx: dict,collection_id:str,outfile, pretty:bool =False):
    """ Get Metadata for single Collection from its ID"""
    collection=_get_json_response_from_signed_request(f"collections/{id}" , f"Collection {id}", method="GET")
    if pretty:
        outfile.write(json.dumps(collection, indent=2))
    else:
        outfile.write(json.dumps(collection))
    print("done")


@item.command("get")
@click.argument("collection_id", type=str)
@click.argument("item_id",type=str)
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.option("-f", "--file","outfile",type=click.File('w', encoding='utf8'), help='Output file.', default=click.get_text_stream('stdout'))
@click.pass_context
def get_item(ctx: dict, collection_id:str, item_id:str, outfile, pretty:bool =False):
    """ Get Metadata for single Collection from Collection ID and Item ID"""
    collection=_get_json_response_from_signed_request(f"collections/{collection_id}/items/{item_id}" , f"Item {item_id} from Collection {collection_id}", method="GET")
    if pretty:
        outfile.write(json.dumps(collection, indent=2))
    else:
        outfile.write(json.dumps(collection))
    print("done")






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