import argparse
import sys
from .stac_api_cli import  TerrApiStac

class TerrApi(object):
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            description='Terrabyte API CMD Tool',
            usage='''terrApi <command> [<args>]

                Currently supported commands are:
                stac     Interact with terrabyte STAC Services
                slurm    Submit Jobs via REST-API
                ''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args =parser.parse_args(["stac"])
       # args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)(sys.argv[2:])
    
    def slurm(self, argv):
        print("Not implemented yet")
        exit(0)
    def stac(self,argv):
        TerrApiStac(argv)
        exit(0)

       





if __name__ == '__main__':
    TerrApi()
       