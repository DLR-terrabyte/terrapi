from argparse import ArgumentParser
from .argparse_decorator import argument, subcommand
from typing import Optional
import sys
import json

from typing import Optional, Union
import requests

from .settings import TERRABYTE_AUTH_URL, TERRABYTE_PRIVATE_API_URL, TERRABYTE_CLIENT_ID
from .auth.config import RefreshTokenStore
from .auth.oidc import (
    OidcDeviceAuthenticator,
    AccessTokenResult,
    OidcClientInfo,
    OidcProviderInfo,
)

#if needed simple stac maipulation functions
# https://github.com/EOEPCA/open-science-catalog-builder/blob/main/osc_builder/mystac.py 


class TerrApiStac(object):
    tokens: Optional[AccessTokenResult]
    stac_parser = ArgumentParser()
    stac_subparsers = stac_parser.add_subparsers(dest="subcommand")
    #add general arguments here 
    #toDo which global switches to add?

    def __init__(self, argv: list) -> None:
        self.args = TerrApiStac.stac_parser.parse_args(argv)
        self.tokens = None
        self.auth = OidcDeviceAuthenticator(
            OidcClientInfo(
                client_id=TERRABYTE_CLIENT_ID,
                provider=OidcProviderInfo(
                    issuer=TERRABYTE_AUTH_URL,
                ),
            ),
            use_pkce=True)





        if self.args.subcommand is None:
            TerrApiStac.stac_parser.print_help()
        else:
            self.args.func(self)

    

    @subcommand([argument("id", )], parent=stac_subparsers)
    def deleteCollection(self):
        print("toDo")

    @subcommand([argument()], parent=stac_subparsers)
    def updateCollection(self):
        print("toDo")

    @subcommand([argument()], parent=stac_subparsers)
    def createCollection(self):
        print("toDo")
    
    @subcommand([argument("-f", "--force", action='store_true',help="Force a new 2FA Login, even if the current Refresh Token is still valid")], parent=stac_subparsers)
    def login(self):
        if self.args.force:
            print("force")
        print("toDo")



