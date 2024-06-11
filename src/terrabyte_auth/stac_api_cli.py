import click
import sys
import json
import ast
import re
import jwt
from datetime import datetime, timezone, timedelta
import traceback

from typing import Optional, Union, List
import requests
from urllib.parse import urlparse, urlunparse

from .settings import TERRABYTE_AUTH_URL, TERRABYTE_PRIVATE_API_URL, TERRABYTE_CLIENT_ID, TERRABYTE_PUBLIC_API_URL

from .auth.config import RefreshTokenStore
from .auth.oidc import (
    OidcDeviceAuthenticator,
    AccessTokenResult,
    OidcClientInfo,
    OidcProviderInfo,
)

from .adapter import wrap_request

stacClientId = TERRABYTE_CLIENT_ID
privateStacUrl = TERRABYTE_PRIVATE_API_URL
publicStacUrl = TERRABYTE_PUBLIC_API_URL
debugCli = False
goPublic = False
tokenStore=RefreshTokenStore()
#add additial scopes to request eg for slurm
#oidScopes=["slurmrest"]
oidScopes=None

#if needed simple stac maipulation functions
# https://github.com/EOEPCA/open-science-catalog-builder/blob/main/osc_builder/mystac.py 

#helper funtions
def _get_device_authenticator(client_id:str, scopes:List[str]=None)->OidcDeviceAuthenticator:
    return OidcDeviceAuthenticator(
                OidcClientInfo(
                    client_id = client_id,
                    provider = OidcProviderInfo(
                        issuer = TERRABYTE_AUTH_URL,
                        scopes = scopes
                    ),
                ),
                use_pkce=True,
            )


def _get_issuer(url: str) ->str:
    issuer = urlunparse(
                urlparse(url)._replace(path="", query="", fragment="")
            )
    return issuer

def _get_json_response_from_signed_request(stac_path:str, error_desc:str, method="GET",alt_method: str = None,alt_code:int =-1, **kwargs)->dict:
    url=f"{privateStacUrl}/{stac_path}" 
    if goPublic: url=f"{publicStacUrl}/{stac_path}"
    if debugCli:  print(f" Requesting {error_desc} from {url} using {method}")
    try:   
        if goPublic: r = requests.request(url=url, method=method, **kwargs)
        else:  r=wrap_request(requests.session(),url=url,client_id=stacClientId,method=method,**kwargs)      
        #check if request was successful 
        #toDO Dinstinquish errors for differnt codes
        # see https://github.com/stac-utils/stac-fastapi/blob/add05de82f745a717b674ada796db0e9f7153e27/stac_fastapi/api/stac_fastapi/api/errors.py#L23
        #fastAPI errors:
        if alt_method and r.status_code == alt_code :
            if debugCli: click.echo(f"Request to {url} using {method} failed with error Code 409. Retrying with  {alt_method}",err=True)
            r2=wrap_request(requests.session(),url=url,client_id=stacClientId,method=alt_method,**kwargs)
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
                 if debugCli: click.echo(f"Response was: {json_stac}")
                 return None
            case 424:
                
                click.echo(f"Stac API reported a Database Error ({r.status_code}) when calling {url}, Message: {message}", err=True)
                return None
            case 500:
                click.echo(f"Stac API reported an Internal Server Error ({r.status_code}) when calling {url}, Message: {message}", err=True)
                click.echo(f" Please retry again in a few Minutes and please report the issue to the terrabyte supportdesk if it persists.", err=True)
                return None        
        r.raise_for_status()
        #toDo maybe check size for 0?
        json_stac=r.json()
        return json_stac
       
    except Exception as e:
        click.echo(f"Requesting {error_desc} from URL {url} failed")
        if debugCli:
            click.echo(f"Error reported was:")
            click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            traceback.print_exc()
        return None

def _readJson_from_file_or_str(json_str:str = None, inputfile = None) ->dict:
    if (inputfile is None and json_str is None) or (inputfile and json_str):
        click.echo("Error. Either JSON String or JSON File have to be specified. Exiting",err=True)
        exit(4)
        
    if inputfile: 
        try: json_dict=json.loads(inputfile)
        except:
           #fallback to also try reading it via ast?
           click.echo(f"Failed to import valid JSON from File {inputfile.name}. Exiting",err=True)
           exit(5)
        return json_dict
    if json_str: 
        try:
            json_dict=json.loads(json_str)
            return json_dict
        except Exception:
            try:
                if debugCli: click.echo("json.loads failed. Falling back to ask convert", err=True)
                json_dict = ast.literal_eval(json_str)
            except Exception:
                click.echo(f"Failed to convert the String {json_str} to valid JSON. Exiting",err=True)
                exit(5)
    #should never be reached
    return {}

def _get_auth_refresh_tokens(noninteractive:bool=False, force_renew: bool =False):
    stac_issuer = _get_issuer(privateStacUrl)
    if debugCli: click.echo(f"Scopes are: {oidScopes}")
    auth = _get_device_authenticator(client_id=stacClientId, scopes=oidScopes)
    if force_renew:
        refresh_token = None
    else:
        refresh_token = tokenStore.get_refresh_token_not_expired(issuer=stac_issuer, client_id=stacClientId)
   
    if refresh_token:
        try:
            if debugCli: click.echo(f"Trying to obtain Tokens with stored Refresh Token")
            tokens = auth.get_tokens_from_refresh_token(refresh_token=refresh_token)
            if debugCli: click.echo(f"successfully obtained valid Refresh Token")
        except Exception as e:
           if debugCli:
             click.echo(f"Accessing Token with stored Refresh Token failed.")
             click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
           refresh_token=None
           if noninteractive:
               return None
    if refresh_token == None:
        try:
            tokens = auth.get_tokens(True)
            if debugCli: click.echo(f"Storing Refresh token to file.")
            tokenStore.set_refresh_token(issuer=stac_issuer, client_id=stacClientId, refresh_token=tokens.refresh_token)
        except Exception as e:
            click.echo("Login to the 2FA terrabyte System failed. The Error returned was: " )
            click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            return None
    return tokens

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
    if user_id: rw_prefix.insert(0, user_id+".")
    return rw_prefix, ro_prefix


@click.group()
@click.option("-p", "--public",default=False, is_flag = True, show_default = False, help="Switch to public API")
@click.option("--debug",  is_flag = True, show_default = False, default = False, help="be more verbose", hidden=True)
@click.option("--privateURL","private_url",type=str,   show_default = False, default = None, help="overwrite private Stac URL.  Warning expert OPTION! ")
@click.option("--publicURL","public_url",type=str,   show_default = False, default = None, help="overwrite public Stac URL.  Warning expert OPTION! ")
@click.option("--clientID", "client_id",type=str, default = stacClientId, help="overwrite clientID", hidden=True)
@click.option("--scope", "scope",type=str,default = None, help="add scope, seperate multiple with ','", hidden=True)
def stac(debug: bool = False, public: bool = False ,private_url:str = None, public_url:str = None, client_id:str=None, scope:str=None):
    """Command Line for terrabyte private STAC API"""
    global debugCli
    global goPublic
    global privateStacUrl
    global publicStacUrl
    global stacClientId
    global oidScopes

    if debug:
        
        debugCli=True
        click.echo("Activating debug")
    if private_url:
        privateStacUrl=private_url
        if debugCli: click.echo(f"Api URl is now {privateStacUrl}")
    
    if public_url:
        publicStacUrl=public_url
        goPublic=True
        if debugCli: click.echo(f"Api URl is now {publicStacUrl}")
    if public:
        if debugCli: click.echo("Switching to public STAC API. Update/modify not possible")
        goPublic=True
        if debugCli: click.echo(f"Api URl is now {publicStacUrl}")
    if client_id:
        if debugCli: click.echo(f"Client ID is now {client_id}")
        stacClientId=client_id
    if scope:
        oidScopes=scope.split(",")
        if debugCli: click.echo(f"Adding Scope(s): {oidScopes}")
        #oidScopes=[scope]
    pass

#define subcommands
@click.group()
def collection():
    """ Interact with STAC Collection(s)"""
    #print("in Collection")
    pass

@click.group()
def item():
    """ Interact with Stac Item(s)"""
    pass



@collection.command()
@click.option("-f","--filter",type=str, default="", help="Filter Collection ID with regex")
@click.option("-t", "--title",default=False, is_flag = True, show_default = False, help="Add Title to output")
@click.option("-d", "--description",default=False, is_flag = True, show_default = False, help="Add Description to output")
def list(filter: str ="", title: bool = False, description: bool = False):
    """ List Collections"""
     
    collections=_get_json_response_from_signed_request("collections", "Collections")['collections']
        
    for collection in collections:
        if re.search(filter, collection['id']):
            click.echo(collection['id'])
            if title and 'title' in collection:
                click.echo(f"title= '{collection['title']}'")
            if description and 'description' in collection:
                click.echo(f"description= '{collection['description']}'")
                click.echo("")
    
@item.command("list")
@click.option("-f","--filter",type=str, default="", help="Filter Item ID with regex")
@click.option("-a", "--all",default=False, is_flag = True, show_default = False, help="Print whole Stac Item")
@click.option("-p", "--pretty",default=False, is_flag = True, show_default = False, help="Indent")
#@click.option("-d", "--description",default=False, is_flag = True, show_default = False, help="Add Description to output")
@click.argument("collection_id", type=str)
def list_item(collection_id:str, filter: str ="", all: bool = False, pretty: bool = False):
    """ List Items in Collection """
     
    featureCollection=_get_json_response_from_signed_request(f"collections/{collection_id}/items", f"Items in Collection {collection_id}")
    #['collections']
   # click.echo(json.dumps(featureCollection['features'],indent=2))
    items=featureCollection.get('features')
    indent=0
    if pretty: indent=2
    if items:
        for item in items:
            if re.search(filter, item['id']):
                if all: 
                    click.echo(json.dumps(item,indent=indent))
                else: click.echo(item['id'])


@collection.command()
@click.argument("collection_id")
@click.confirmation_option(help='Confirm deletion.', prompt='Are you sure you want to delete the Collection?')
def delete(collection_id:str):
    """ Delete a Collection defined by its ID"""
    if goPublic:
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
def delete_item(collection_id:str, item_id:str):
    """ Delete an Item from Collection"""
    if goPublic:
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
def create(id: str = None, json_str: str = None, inputfile = None,update: bool = False ):
    """Create a Collection from either String or File"""
    if goPublic:
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
    response=_get_json_response_from_signed_request(f"collections" , f"Create Collection {id}", method="POST",alt_method=alt_method,alt_code=alt_code, json=collection)
    click.echo(json.dumps(response))

@item.command("create")
@click.argument("collection_id", type=str)
@click.option("--id","item_id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
#@click.option("-u", "--update",default=False, is_flag = True, show_default = False,help='Update Collection if it allready exists')
def create_item(collection_id:str,item_id: str = None, json_str: str = None, inputfile = None,update: bool = False ):
    """Create a new Item in Collection from either String or File"""
    if goPublic:
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
    if response: click.echo(json.dumps(response))


@collection.command()
@click.option("--id",default=None,type=str, help="ID of the Collection. If specified will overwrite the ID in the Collection JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
def update(id: str = None, json_str: str = None, inputfile = None):
    """Update an existing Collection from either String or File"""
    if goPublic:
       click.echo("ERROR! Update is only possible for private stac API. Exiting", err=True)
       exit(3)
    collection=_readJson_from_file_or_str(json_str,inputfile)
    #toDo maybe add some checks for ID and if has minimum STAC Collection requirements 
    if id:
        collection['id']=id
    else:
        id=collection.get('id')
    response=_get_json_response_from_signed_request(f"collections" , f"Update Collection {id}", method="PUT", json=collection)
    if response: click.echo(json.dumps(response))
      
@item.command("update")
@click.argument("collection_id", type=str)
@click.option("--id","item_id",default=None,type=str, help="ID of the Item. If specified will overwrite the ID in the Item JSON")
@click.option("-j","--json","json_str",default=None, type=str, help="Provide collection as JSON String")
@click.option("-f", "--file","inputfile",default=None,type=click.File('r', encoding='utf8'), help='Read Collection JSON from File. Specify - to read from pipe')
def update_item(collection_id:str,item_id: str = None, json_str: str = None, inputfile = None):
    """Update an existing Item from either String or File"""
    if goPublic:
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
    if response: click.echo(json.dumps(response))
      




@collection.command()
@click.argument("collection_id", type=str)
@click.option("-p", "--pretty", default=False, is_flag = True, show_default = False, help="print pretty readable json")
@click.option("-f", "--file","outfile",type=click.File('w', encoding='utf8'), help='Output file.', default=click.get_text_stream('stdout'))
def get(collection_id:str,outfile, pretty:bool =False):
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
def get_item(collection_id:str,item_id:str,outfile, pretty:bool =False):
    """ Get Metadata for single Collection from Collection ID and Item ID"""
    collection=_get_json_response_from_signed_request(f"collections/{collection_id}/items/{item_id}" , f"Item {item_id} from Collection {collection_id}", method="GET")
    if pretty:
        outfile.write(json.dumps(collection, indent=2))
    else:
        outfile.write(json.dumps(collection))
    print("done")


@stac.command()
@click.option("-n", "--noninteractive",  is_flag=True, show_default=False, default=False,help="Fail if no valid Refresh Token stored")
@click.option("-g", "--gdal",  is_flag=True, show_default=False, default=False,help="Add Options needed by gdal")
@click.option("-c", "--curl",  is_flag=True, show_default=False, default=False,help="Add Options needed by curl")
@click.option("-w", "--wget",  is_flag=True, show_default=False, default=False,help="Add Options needed by wget")
def auth(wget:bool =False, gdal: bool = False, curl: bool = False, noninteractive:bool = False)->None:
    """ Print the single use auth token needed to directly interact with the private STAC API"""
    tokens = _get_auth_refresh_tokens(noninteractive)
    if tokens:
        if wget: 
            print(f' --header="Authorization:  {tokens.access_token}" ')
            return
        if curl: 
            print(f' -H "Authorization: Bearer {tokens.access_token}" ')
            return
        if gdal:
            print(f'GDAL_HTTP_BEARER={tokens.access_token} ')
            return
        print(tokens.access_token)
    else: exit(1)
    


@stac.command()
@click.option("-f", "--force", is_flag=True, show_default=False, default=False, help="Force new login, even if valid Refresh Token stored" )
@click.option("--valid", is_flag=True, type=bool,  show_default=False,default=False, help="Will print till when the Refresh token is valid.")
@click.option( "--delete", is_flag=True, show_default=False, help="Delete existing Refresh Token. Will remove the Refresh token if it exists and then exit", default=False )
@click.option("-d", "--days", type=int,  show_default=False,default=0,help="Min Nr of days the Token still has to be valid. Will refresh Token if it expires earlier")
@click.option("-h", "--hours", type=int, show_default=False, default=0,help="Min Nr of hours the Token still has be valid. Will refresh Token if it expires earlier")
@click.option("-t","--till", type=click.DateTime(), default=datetime.now(), help="Date the Refresh token has to be still be valid. Will refresh Token if it expires earlier")
@click.option("--allowedPrefix","print_prefix", is_flag=True, show_default=False, help="Print list of readable/writable Collection Prefixes")
def login(force: bool = False, delete: bool = False, days: int = 0, hours: int = 0, till: Optional[datetime] =datetime.now(), valid: bool = False , print_prefix: bool=False):
    """Interactively login via 2FA to obtain refresh Token for the STAC API. 
    A Valid Refresh token is needed for all the other sub commands"""
    #if debugCli: click.echo("Logging in")
    stac_issuer=_get_issuer(privateStacUrl)
    till = max(till, datetime.now()+timedelta(hours=hours, days=days)) 
    if valid:
        validity= tokenStore.get_expiry_date_refresh_token(stac_issuer, stacClientId)
        if validity:
            click.echo(f"Refresh Token valid till: {validity.astimezone()}")
        else:
            click.echo(f"No valid Refresh Token on file") 
        return 
    if delete:
        if debugCli: click.echo("Deleting Refresh Token")
        tokenStore.delete_refresh_token(stac_issuer, stacClientId)
        return
    tokens = _get_auth_refresh_tokens(force_renew=force)
    if tokens is None:
        exit(1)
    if(print_prefix): 
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

if __name__ == '__main__':
    stac()