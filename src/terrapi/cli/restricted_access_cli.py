import click
from .shared_cli import login, auth
from ..adapter import wrap_request
from ..settings import  TERRABYTE_RESTRICTED_DATA_API_URL, TERRABYTE_TESTING_RESTRICTED_DATA_API_URL
import requests
from terminaltables import AsciiTable

@click.group()
@click.pass_context
@click.option("-l", "local", help="Development Option to talk to backend locally (port 8000) ", default=False, type=bool, is_flag=True)
@click.option("-t", "testing", help="Development Option to talk to testing backend ", default=False, type=bool, is_flag=True)
def restricted_data(ctx: dict, local: bool, testing: bool):
    """ Self Register to restricted Datasets on DSS. 
        This tool allows you to get an overview of currently available restricted datasets, your current access status and their usage restrictions/requirements. 
        Request access to datasets by accepting their specific EULAs 
    """
    ctx.ensure_object(dict)
    ctx.obj['privateAPIUrl'] = TERRABYTE_RESTRICTED_DATA_API_URL
    if testing:
        click.echo("Switching to development backend")
        ctx.obj['privateAPIUrl'] = TERRABYTE_TESTING_RESTRICTED_DATA_API_URL
    if local:
        click.echo("Switching to local backend") 
        ctx.obj['privateAPIUrl'] = "http://localhost:8000"

@restricted_data.command()
@click.pass_context
def list_available(ctx: dict):
    """List all restricted datasets available on Terrabyte DSS.
    This command shows datasets you are eligible to access and their current status.
    """

    url = f"{ctx.obj['privateAPIUrl']}/list-available-DSS"
    response=None
    containers=None
    if ctx.obj['DEBUG']:
        click.echo(f"Accessing {url} via GET")
    try:
        r = wrap_request(requests.sessions.Session(), url=url, client_id=ctx.obj['ClientId'], method="GET")
        r.raise_for_status()
        response = r.json()
    except requests.exceptions.HTTPError as http_err:
        click.echo(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        click.echo(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        click.echo(f"Timeout error occurred: {timeout_err}")
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}")
    if response:
        if isinstance(response,dict):
            containers=response.get("containers")
        else:
           containers=None  
    if containers:
        table_data = [['Name','ID', 'status']]
        for container in containers:
            line=[container.get('name'), container.get('id'), container.get('status')]
            table_data.append(line )
        table = AsciiTable(table_data)
        click.echo(table.table)


def get_container_info(ctx: dict, dataset: str) -> dict:
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
def request_access(ctx: dict, dataset: str) -> None:
    """Request access to a specific dataset on Terrabyte DSS.

    This command allows you to interactively request access to a dataset by accepting its End User License Agreement (EULA).
    The dataset can be specified by its ID or name. Some datasets may be restricted to specific user groups (e.g., DLR employees, specific Insitutes or Departments).

    Steps:
    - Displays the dataset's details, including its name, ID, description, and associated documents.
    - Prompts you to confirm that you have read and accepted the EULA.
    - Sends a request to the backend to grant access to the dataset.

    Example:
    terrapi restricted-data request-access <dataset-id-or-name>
    """
    accessurl = f"{ctx.obj['privateAPIUrl']}/request/access/{dataset}"
    container = get_container_info(ctx, dataset)
    if not container:
        return
    status = container.get("status", "")
    if status == "registered":
        click.echo(f"You already have access to the container {container['name']} and its DSS {container['id']}.What more do you need?")
        return
    if status == "not-allowed":
        click.echo(f"Unfortunately, your account is not eligible for the container {container['name']}.")
        return
    if status == "available":
        click.echo(f"You are requesting {container['access']} access to the DSS Container {container['name']}.")
        click.echo("Please read the following description and the specified documents thoroughly:")
        click.echo(f"Container Name:       {container['name']}")
        click.echo(f"Container DSS ID:     {container['id']}")
        click.echo("Container Documents:")
        for href in container["hrefs"]:
            click.echo(f"{href}")
        click.echo(f"\nContainer Description: \n\n {container['description']}")
        click.echo("####################################################\n")
        eulaAccept = click.confirm(
            f"Do you confirm that you have read the License Agreement of the container {container['name']} and that you accept the stated terms and conditions?",
            default=False,
            show_default=False,
        )
        if not eulaAccept:
            click.echo("As you have not accepted the License Agreement, we cannot request access. Sorry.")
            return

    click.echo("")
    click.echo(f"EULA accepted. Requesting access to container {container['name']}.")
    success = None
    try:
        if ctx.obj['DEBUG']:
            click.echo(f"Accessing {accessurl}?eulaAccept={eulaAccept} via POST")
        r = wrap_request(
            requests.sessions.Session(),
            url=f"{accessurl}?eulaAccept={eulaAccept}",
            client_id=ctx.obj['ClientId'],
            method="POST",
        )

        if r.status_code == 500:
            click.echo(
                "Error: Backend reported an internal server error (500). Please try again later or contact the Terrabyte Helpdesk at servicedesk@terrabyte.lrz.de if the error persists."
            )
        else:
            if 200 <= r.status_code < 299:
                response = r.json()
                success = response.get("status", None)
            else:
                click.echo(
                    f"Error: Received status code {r.status_code} from the backend. Details: {r.json().get('detail', r.json())}"
                )
    except Exception as e:
        click.echo(f"Unhandled exception: {e}")
    if success:
        click.echo(f"Status of access request: {success}")


@restricted_data.command()
@click.argument('dataset')
@click.pass_context
def request_info(ctx: dict, dataset: str):
    """Get detailed information about a dataset container.

    This command retrieves and displays detailed information about a dataset container, including:
    - Name
    - DSS ID
    - Associated documents (e.g., EULAs or descriptions)
    - A detailed description of the dataset

    The dataset can be specified by its ID or name.

    Example:
    terrapi restricted-data request-info <dataset-id-or-name>
    """
    container = get_container_info(ctx, dataset)
    if container:
        click.echo(f"Container Name:       {container['name']}")
        click.echo(f"Container DSS ID:     {container['id']}")
        click.echo("Container Documents:")
        for href in container['hrefs']:
            click.echo(f"{href}")
        click.echo(f"\nContainer Description: \n\n {container['description']}")


restricted_data.add_command(login)
restricted_data.add_command(auth)







