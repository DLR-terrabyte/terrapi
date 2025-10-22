import click
from .stac_api_cli import stac
from .restricted_access_cli import restricted_data
from ..settings import TERRABYTE_PRIVATE_API_URL, TERRABYTE_CLIENT_ID
from ..auth.config import RefreshTokenStore
from .. import __version__  # Import version from __init__.py


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--debug/--no-debug', '-d/-nd', default=False, help="Activate verbose outputs for debugging purposes.", hidden=True)
@click.version_option(version=__version__, prog_name="terrapi", message="%(prog)s version %(version)s")
@click.pass_context
def terrapi(ctx, debug):
    """Terrabyte API Command Line Tool (terrapi)

    The Terrabyte client library (terrapi) is a command-line interface (CLI) 
    designed to help users interact with protected Terrabyte Application Programming Interfaces (APIs). 

    Features:
    - User authentication via 2FA website redirection.
    - Caching of long-lived refresh tokens in the user's home directory for future API calls.
    - Support for specific APIs implemented as subcommands.

    Use `terrapi --help` to see available commands and options.
    """
    ctx.ensure_object(dict)

    # Add some defaults to make sure login and auth work for all subcommands. Overwrite in subcommands where appropriate.
    ctx.obj['privateAPIUrl'] = TERRABYTE_PRIVATE_API_URL
    ctx.obj['ClientId'] = TERRABYTE_CLIENT_ID
    ctx.obj['oidScopes'] = None
    ctx.obj['tokenStore'] = RefreshTokenStore()
    ctx.obj['DEBUG'] = debug

    if debug:
        click.echo("Debug mode activated.")


@click.command()
@click.pass_context
def slurm(ctx):
    """SLURM REST API (Coming Soon)

    This command will provide access to the SLURM REST API in the future.
    Stay tuned for updates!
    """
    ctx.obj['oidScopes'] = ["slurmrest"]
    if ctx.obj['DEBUG']:
        click.echo("SLURM REST API is not implemented yet.")


# Add subcommands to the main CLI group
terrapi.add_command(stac)
# terrapi.add_command(slurm)  # Uncomment when SLURM is implemented
terrapi.add_command(restricted_data)


if __name__ == '__main__':
     terrapi(obj={})



