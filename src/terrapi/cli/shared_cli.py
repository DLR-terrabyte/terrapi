import click
from .. auth.oidc import (
    OidcDeviceAuthenticator,
    OidcClientInfo,
    OidcProviderInfo,
)
from .. settings import TERRABYTE_AUTH_URL
from urllib.parse import urlparse, urlunparse
from typing import  List
from datetime import datetime, timedelta

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

def _get_auth_refresh_tokens(ctx:dict, noninteractive:bool=False, force_renew: bool =False, notExpiredBefore=datetime.now()):
    stac_issuer = _get_issuer(ctx.obj['privateAPIUrl'])
    debugCli=ctx.obj['DEBUG']
    if debugCli: 
        click.echo(f"Scopes are: {ctx.obj['oidScopes']}")
    auth = _get_device_authenticator(client_id=ctx.obj['ClientId'], scopes=ctx.obj['oidScopes'])
    if force_renew:
        refresh_token = None
    else:
        refresh_token =  ctx.obj['tokenStore'].get_refresh_token_not_expired(issuer=stac_issuer, client_id=ctx.obj['ClientId'], than=notExpiredBefore)
   
    if refresh_token:
        try:
            if debugCli: 
                click.echo(f"Trying to obtain Tokens with stored Refresh Token for client_id={ctx.obj['ClientId']}")
            tokens = auth.get_tokens_from_refresh_token(refresh_token=refresh_token)
            if debugCli:
                click.echo("successfully obtained valid Refresh Token")
        except Exception as e:
           if debugCli:
             click.echo("Accessing Token with stored Refresh Token failed.")
             click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
           refresh_token=None
           if noninteractive:
               return None
    if refresh_token is None:
        try:
            tokens = auth.get_tokens(True)
            if debugCli:
                click.echo("Storing Refresh token to file.")
            ctx.obj['tokenStore'].set_refresh_token(issuer=stac_issuer, client_id=ctx.obj['ClientId'], refresh_token=tokens.refresh_token)
        except Exception as e:
            click.echo("Login to the 2FA terrabyte System failed. The Error returned was: " )
            click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
            return None
    return tokens


@click.command()
@click.option("-n", "--noninteractive",  is_flag=True, show_default=False, default=False,help="Fail if no valid Refresh Token stored")
@click.option("-g", "--gdal",  is_flag=True, show_default=False, default=False,help="Add Options needed by gdal")
@click.option("-c", "--curl",  is_flag=True, show_default=False, default=False,help="Add Options needed by curl")
@click.option("-w", "--wget",  is_flag=True, show_default=False, default=False,help="Add Options needed by wget")
@click.pass_context
def auth(ctx: dict, wget:bool =False, gdal: bool = False, curl: bool = False, noninteractive:bool = False)->None:
    """ Print the single use auth token needed to directly interact with the private API"""
    tokens = _get_auth_refresh_tokens(ctx,noninteractive)
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
    else:
        exit(1)
    




@click.command()
@click.option("-f", "--force", is_flag=True, show_default=False, default=False, help="Force new login, discarding any existing tokens" )
@click.option("-v", "--valid", is_flag=True, type=bool,  show_default=False,default=False, help="Will print till till when the Refresh token is valid.")
@click.option( "--delete", is_flag=True, show_default=False, help="Delete existing Refresh Token. Will remove the Refresh token if it exists and then exit", default=False )
@click.option("-d", "--days", type=int,  show_default=False,default=0,help="Min Nr of days the Token still has to be valid. Will refresh Token if it expires earlier")
@click.option("-h", "--hours", type=int, show_default=False, default=0,help="Min Nr of hours the Token still has be valid. Will refresh Token if it expires earlier")
@click.option("-t","--till", type=click.DateTime(), default=None, help="Date the Refresh token has to be still be valid. Will refresh Token if it expires earlier")
@click.pass_context
def login(ctx: dict, force: bool = False, delete: bool = False, days: int = 0, hours: int = 0, till: datetime = datetime.now() , valid: bool = False ):
    """Interactively login via 2FA 
    to obtain refresh Token for the API. 
    A Valid Refresh token is needed for all the other sub commands
    It is recommended to call this function first to make sure you have a valid token for the remainder of your job. This allows the other subcommands to run non inveractive    
    """
    if ctx.obj['DEBUG']:
        click.echo(f"Till is: {till}")
    stac_issuer=_get_issuer(ctx.obj['privateAPIUrl'])
    validTill=datetime.now()+timedelta(hours=hours, days=days)
    if till:
         validTill = max(till,validTill ) 
   
    if ctx.obj['DEBUG']:
        click.echo(f"validTill is: {validTill}")
    if valid:
        validity= ctx.obj['tokenStore'].get_expiry_date_refresh_token(stac_issuer, ctx.obj['ClientId'])
        if validity:
            click.echo(f"Refresh Token valid till: {validity.astimezone()}")
        else:
            click.echo("No valid Refresh Token on file") 
        return 
    if delete:
        if ctx.obj['DEBUG']:
            click.echo("Deleting Refresh Token")
        ctx.obj['tokenStore'].delete_refresh_token(stac_issuer, ctx.obj['ClientId'])
        return
    tokens = _get_auth_refresh_tokens(ctx,force_renew=force, notExpiredBefore=validTill)
    if tokens is None:
        exit(1)
