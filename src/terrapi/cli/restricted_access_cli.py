import click
from .shared_cli import login, auth
from ..adapter import wrap_request
from ..settings import  TERRABYTE_RESTRICTED_DATA_API_URL
import requests
import json
from terminaltables import AsciiTable

@click.group()
@click.pass_context
def restricted_data(ctx:dict):
    """ Self Register to restricted Datasets on DSS. 
        This tool allows you to get an overview of currently available restricted datasets, your current access status and their usage restrictions/requirements. 
        Request access to datasets by accepting the specific EULAs 
    """

    ctx.obj['privateAPIUrl'] = TERRABYTE_RESTRICTED_DATA_API_URL
    ctx.obj['privateAPIUrl'] = "http://127.0.0.1:8000"
    pass

@restricted_data.command()
@click.pass_context
def list_available(ctx:dict):
    """ List currently available restricted Datasets on terrabyte"""


    url = f"{ctx.obj['privateAPIUrl']}/list-available-DSS"
    response=None
    containers=None

    try:   
       r=wrap_request(requests.sessions.Session(),url=url,client_id=ctx.obj['ClientId'],method="GET")
       r.raise_for_status()
       response=r.json()
    except Exception as e:
         click.echo(f"{e}")
       # click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
    if response:
        containers=response.get("containers")
    if containers:
        table_data = [["Name","ID", "status"]]
        for container in containers:
            line=[container['name'], container['id'], container['status']]
            table_data.append(line )
        table = AsciiTable(table_data)
        click.echo(table.table)


@restricted_data.command()
@click.argument('dataset')
@click.pass_context
def request_access(ctx:dict,dataset:str):
    """ Interactively request access to specific dataset on terrabyte DSS by accepting its EULAs 
        Dataset can be provided by its ID or name
    """
    pass

@restricted_data.command()
@click.argument('dataset')
@click.pass_context
def container_info(ctx:dict,dataset:str):
    """ Interactively request access to specific dataset on terrabyte DSS by accepting its EULAs 
        Dataset can be specfied either by its ID or its name
    """
    url = f"{ctx.obj['privateAPIUrl']}/request/container/{dataset}"
    response=None
    container=None
    try:   
       r=wrap_request(requests.sessions.Session(),url=url,client_id=ctx.obj['ClientId'],method="GET")
       r.raise_for_status()
       response=r.json()
    except Exception as e:
         click.echo(f"{e}")
       # click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
    if response:
        container=response.get("container")
        click.echo(f"Container Name:       {container["name"]}")
        click.echo(f"Container ID:         {container["id"]}")
        click.echo(f"Container Documents:  {container["hrefs"]}")
        for href in container["hrefs"]:
            click.echo(f"                      {href}")
            #click.launch(href)
        click.echo(f"Container Description: \n {container["description"]}")
        


restricted_data.add_command(login)
#restricted_data.add_command(auth)







