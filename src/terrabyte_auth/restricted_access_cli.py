import click
from .shared_cli import login

@click.group()
@click.pass_context
def restricted_data(ctx:dict):
    """" Self Register to restricted Dataset. 
         Get an overview of available datasets and their usage restrictions/requirements. 
         Register to datasets by accepting the specific EULAs 
    """
    pass

@restricted_data.command()
@click.pass_context
def list_available(ctx:dict):
    """ To implement"""
    pass 

@restricted_data.command()
@click.pass_context
def request_access(ctx:dict):
    """ To implement"""
    pass


restricted_data.add_command(login)







