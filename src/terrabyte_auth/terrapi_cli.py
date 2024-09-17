import click
import sys
from .stac_api_cli import  stac


       
@click.group()
@click.option('--debug/--no-debug', default=False, help="be more verbose", hidden=True)
@click.pass_context
def terrapi(ctx, debug):
    """Terrabyte API CMD Tool """   
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    if debug: 
         click.echo("Activating debug")

@click.command()
@click.pass_context
def slurm(ctx):
    """ SLURM REST API coming soon """
    ctx.obj['oidScopes']=["slurmrest"]
    if ctx.obj['DEBUG']:
        click.echo("Not implemented yet")


terrapi.add_command(stac)
terrapi.add_command(slurm)


if __name__ == '__main__':
    terrapi(obj={})
       