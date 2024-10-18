import click
from .shared_cli import login, auth

@click.group()
@click.pass_context
def restricted_data(ctx:dict):
    """ Self Register to restricted Datasets on DSS. 
        This tool allows you to get an overview of currently available restricted datasets, your current access status and their usage restrictions/requirements. 
        Request access to datasets by accepting the specific EULAs 
    """
    pass

@restricted_data.command()
@click.pass_context
def list_available(ctx:dict):
    """ List currently available restricted Datasets on terrabyte"""
    pass 

@restricted_data.command()
@click.argument('dataset')
@click.pass_context
def request_access(ctx:dict,dataset:str):
    """ Interactively request access to specific dataset on terrabyte DSS by accepting its EULAs 
        Dataset can be provided by its ID or name
    """
    pass


restricted_data.add_command(login)
restricted_data.add_command(auth)







