import click
import sys
from .stac_api_cli import  stac


       
@click.group()
def terrapi():
    """Terrabyte API CMD Tool """   
    pass

@click.command()
def slurm():
    """ SLURM REST API coming soon """


terrapi.add_command(stac)
terrapi.add_command(slurm)


if __name__ == '__main__':
    terrapi()
       