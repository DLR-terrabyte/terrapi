import click
from .shared_cli import login, auth
from ..adapter import wrap_request
from ..settings import  TERRABYTE_RESTRICTED_DATA_API_URL, TERRABYTE_TESTING_RESTRICTED_DATA_API_URL
import requests
from terminaltables import AsciiTable

@click.group()
@click.pass_context
@click.option("-l", "local", help="Development Option to talk to backend locally (localhost:8000) ", default=False,type=bool, is_flag=True)
@click.option("-t", "testing", help="Development Option to talk to testing backend ", default=False,type=bool, is_flag=True)
def restricted_data(ctx:dict,local:bool, testing:bool):
    """ Self Register to restricted Datasets on DSS. 
        This tool allows you to get an overview of currently available restricted datasets, your current access status and their usage restrictions/requirements. 
        Request access to datasets by accepting their specific EULAs 
    """

    ctx.obj['privateAPIUrl'] = TERRABYTE_RESTRICTED_DATA_API_URL
    if testing:
        click.echo("Switching to development backend")
        ctx.obj['privateAPIUrl'] = TERRABYTE_TESTING_RESTRICTED_DATA_API_URL
    if local:
        click.echo("Switching to local backend") 
        ctx.obj['privateAPIUrl'] = "http://localhost:8000"

@restricted_data.command()
@click.pass_context
def list_available(ctx:dict):
    """ List currently available restricted Datasets on terrabyte as well as your eligability """


    url = f"{ctx.obj['privateAPIUrl']}/list-available-DSS"
    response=None
    containers=None
    if ctx.obj['DEBUG']:
        click.echo(f"Accessing {url} via GET")
    try:   
       r=wrap_request(requests.sessions.Session(),url=url,client_id=ctx.obj['ClientId'],method="GET")
       r.raise_for_status()
       response=r.json()
    except Exception as e:
         click.echo(f"{e}")
       # click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
    if response:
        if isinstance(response,dict):
            containers=response.get("containers")
        else:
           containers=None  
    if containers:
        table_data = [["Name","ID", "status"]]
        for container in containers:
            line=[container['name'], container['id'], container['status']]
            table_data.append(line )
        table = AsciiTable(table_data)
        click.echo(table.table)


def get_container_info(ctx:dict,dataset:str)->dict:
    url = f"{ctx.obj['privateAPIUrl']}/request/container/{dataset}"
    if ctx.obj['DEBUG']:
        click.echo(f"Accessing {url} via GET")
    container=None
    try:   
        r=wrap_request(requests.sessions.Session(),url=url,client_id=ctx.obj['ClientId'],method="GET")
        if  r.status_code == 200:
            response=r.json()
            if isinstance(response,dict):
                return response.get("container",None)
            else:
                click.echo(f"Response was : {response}") 
                return response
        match r.status_code:
            case 404:
               click.echo(f"Error requested container '{dataset}' does not exist. Exiting")
               return container 
            
            case 403:
               click.echo(f"Error reported by Backend: {r.json().get('detail')} Exiting")
               return container
            case 500:
                click.echo("Error Backend reported an internal Server Error please try againg later and contact the terrabyte Helpdeskt at servicedesk@terrabyte.lrz.de if the error is ongoing")
                return container
        r.raise_for_status()
       
    except Exception as e:
         click.echo(f"Uncaught Exception Occured: \n{e}")
       # click.echo(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
    return container


@restricted_data.command()
@click.argument('dataset')
@click.pass_context
def request_access(ctx:dict,dataset:str)->None:
    """ Interactively request access to specific dataset on terrabyte DSS by accepting its EULAs 
        Dataset can be provided by its ID or name
        Some datasets might be restriced to DLR Employees
    """
    accessurl = f"{ctx.obj['privateAPIUrl']}/request/access/{dataset}"
    container=get_container_info(ctx,dataset)
    if not container:
        return
    status=container.get("status","")
    if status =="registered":
        click.echo(f"You allready have access to the container {container['name']} and its dss {container['id']}. What more do you need ;-)")
<<<<<<< HEAD
<<<<<<< HEAD
        click.echo(f"You allready have access to the container {container['name']} and its dss {container['id']}. What more do you need ;-)")
=======
>>>>>>> 1e243dd (cleanup after rebase)
        return
    if status =="not-allowed":
        click.echo(f"Unfortunatly your Account is not eligable for the container {container['name']}.")
        return
    if status =="available":
        click.echo(f"You are requesting access to the DSS Container {container['name']}.")
        click.echo("Please read the following Description and the specfied Documents thoroughly")
        click.echo(" ")
        click.echo(f"Container Name:       {container['name']}")
        click.echo(f"Container DSS ID:     {container['id']}")
        click.echo("Container Documents:")
        for href in container["hrefs"]:
            click.echo(f"{href}")
            #click.launch(href)
        click.echo(f"\nContainer Description: \n\n {container['description']}")
        click.echo("####################################################\n") 
        eulaAccept=click.confirm(f"Do you confirm that you have read the Licence Agreement of the container {container['name']} and that you accept the stated terms and contitions?", default=False, show_default =False)
        if not eulaAccept:
            click.echo("As you have not accepted the Licence Agreement, we can not request access. Sorry")
            return
    
    click.echo("")
    click.echo(f"Eula accepted, Requesting access to container {container['name']}")
    success=None
    try:
        if ctx.obj['DEBUG']:
            click.echo(f"Accesing {accessurl}?eulaAccept={eulaAccept} via POST")   
        r=wrap_request(requests.sessions.Session(),url=f"{accessurl}?eulaAccept={eulaAccept}",client_id=ctx.obj['ClientId'],method="POST")
        
        if r.status_code == 500:
            click.echo("Error Backend reported an internal Server Error (500) please try againg later and contact the terrabyte Helpdeskt at servicedesk@terrabyte.lrz.de if the error is ongoing")
        else:
            if r.status_code>=200 and r.status_code<299:
                response=r.json()
                success=response.get("status",None)
            else:
                click.echo(f"Error we received Stauts Code {r.status_code} from the Backend reporting: {r.json().get('detail',r.json())} ")
    except Exception as e:
         click.echo(f"Unhandled Exception {e}")
    if success:
        click.echo(f"Status of access request was: {success}")

        



@restricted_data.command()
@click.argument('dataset')
@click.pass_context
def request_info(ctx:dict,dataset:str):
    """ Get detailed Description of a dataset container
        Dataset can be specfied either by its ID or its name
    """ 
    container=get_container_info(ctx,dataset)
    if container:
        click.echo(f"Container Name:       {container['name']}")
        click.echo(f"Container DSS ID:     {container['id']}")
        click.echo("Container Documents:")
        for href in container['hrefs']:
            click.echo(f"{href}")
            #click.launch(href)
        click.echo(f"\nContainer Description: \n\n {container['description']}")
        

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
        

@restricted_data.command()
@click.argument('dataset')
@click.pass_context
def request_access(ctx:dict,dataset:str)->None:
    """ Interactively request access to specific dataset on terrabyte DSS by accepting its EULAs 
        Dataset can be provided by its ID or name
        Some datasets might be restriced to DLR Employees
    """
    accessurl = f"{ctx.obj['privateAPIUrl']}/request/access/{dataset}"
    container=get_container_info(ctx,dataset)
    if not container:
        return
    status=container.get("status","")
    if status =="registered":
        click.echo(f"You allready have access to the container {container["name"]} and its dss {container["id"]}. What more do you need ;-)")
=======
>>>>>>> c90faac (changed " to ' inside f""prints as it caused issues on linux)
        return
    if status =="not-allowed":
        click.echo(f"Unfortunatly your Account is not eligable for the container {container['name']}.")
        return
    if status =="available":
        click.echo(f"You are requesting access to the DSS Container {container['name']}.")
        click.echo("Please read the following Description and the specfied Documents thoroughly")
        click.echo(" ")
        click.echo(f"Container Name:       {container['name']}")
        click.echo(f"Container DSS ID:     {container['id']}")
        click.echo("Container Documents:")
        for href in container["hrefs"]:
            click.echo(f"{href}")
            #click.launch(href)
        click.echo(f"\nContainer Description: \n\n {container['description']}")
        click.echo("####################################################\n") 
        eulaAccept=click.confirm(f"Do you confirm that you have read the Licence Agreement of the container {container['name']} and that you accept the stated terms and contitions?", default=False, show_default =False)
        if not eulaAccept:
            click.echo("As you have not accepted the Licence Agreement, we can not request access. Sorry")
            return
    
    click.echo("")
    click.echo(f"Eula accepted, Requesting access to container {container['name']}")
    success=None
    try:
        if ctx.obj['DEBUG']:
            click.echo(f"Accesing {accessurl}?eulaAccept={eulaAccept} via POST")   
        r=wrap_request(requests.sessions.Session(),url=f"{accessurl}?eulaAccept={eulaAccept}",client_id=ctx.obj['ClientId'],method="POST")
        
        if r.status_code == 500:
            click.echo("Error Backend reported an internal Server Error (500) please try againg later and contact the terrabyte Helpdeskt at servicedesk@terrabyte.lrz.de if the error is ongoing")
        else:
            if r.status_code>=200 and r.status_code<299:
                response=r.json()
                success=response.get("status",None)
            else:
                click.echo(f"Error we received Stauts Code {r.status_code} from the Backend reporting: {r.json().get('detail',r.json())} ")
    except Exception as e:
         click.echo(f"Unhandled Exception {e}")
    if success:
        click.echo(f"Status of access request was: {success}")

        



@restricted_data.command()
@click.argument('dataset')
@click.pass_context
def request_info(ctx:dict,dataset:str):
    """ Get detailed Description of a dataset container
        Dataset can be specfied either by its ID or its name
    """ 
    container=get_container_info(ctx,dataset)
    if container:
        click.echo(f"Container Name:       {container['name']}")
        click.echo(f"Container DSS ID:     {container['id']}")
        click.echo("Container Documents:")
        for href in container['hrefs']:
            click.echo(f"{href}")
            #click.launch(href)
        click.echo(f"\nContainer Description: \n\n {container['description']}")
        


restricted_data.add_command(login)
#restricted_data.add_command(auth)







