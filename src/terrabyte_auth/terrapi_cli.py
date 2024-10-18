import click
from .stac_api_cli import  stac
from .restricted_access_cli import restricted_data
from .settings import  TERRABYTE_PRIVATE_API_URL, TERRABYTE_CLIENT_ID
from .auth.config import RefreshTokenStore

       
@click.group()
@click.option('--debug/--no-debug', default=False, help="activate verbose outputs", hidden=True)
@click.pass_context
def terrapi(ctx, debug):
    """Terrabyte API CMD Tool: terrapi


     The terrabyte client library terrapi is a small command line interface 
     to support users in interacting with protected terrabyte Application Programming Interfaces (APIs) 
     It encompasses support for user authentication via 2FA website redirection and caches 
     the resulting long lived refresh tokens in the Users Home for use in further API calls.
     
     Specific APIs are implemented as sub commands """   
    ctx.ensure_object(dict)
    # add some defaults to make sure login and auth work for all sub commands. Overwrite in sub command where appropriate
    ctx.obj['privateAPIUrl']=TERRABYTE_PRIVATE_API_URL
    ctx.obj['ClientId']= TERRABYTE_CLIENT_ID
    ctx.obj['oidScopes']=None
    ctx.obj['tokenStore']=RefreshTokenStore()  
    ctx.obj['DEBUG'] = debug


    if debug: 
         click.echo("Activating debug")

@click.command()
#@click.pass_context
def slurm(ctx):
    """ SLURM REST API coming soon """
    ctx.obj['oidScopes']=["slurmrest"]
    if ctx.obj['DEBUG']:
        click.echo("Not implemented yet")


terrapi.add_command(stac)
#terrapi.add_command(slurm)
terrapi.add_command(restricted_data)


if __name__ == '__main__':
    terrapi(obj={})
       