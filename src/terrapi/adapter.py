from typing import Optional
from urllib.parse import urlparse, urlunparse

import requests

from .auth.config import RefreshTokenStore
from .auth.oidc import (
    OidcDeviceAuthenticator,
    AccessTokenResult,
    OidcClientInfo,
    OidcProviderInfo,
)

from .settings import TERRABYTE_AUTH_URL, TERRABYTE_CLIENT_ID


class RequestsAdapter:
    tokens: Optional[AccessTokenResult]

    def __init__(self, auth: OidcDeviceAuthenticator, issuer: Optional[str] = None):
        self.auth = auth
        self.issuer = issuer
        self.tokens = None

    def __call__(self, request: requests.Request) -> Optional[requests.Request]:
        if self.issuer:
            issuer = self.issuer
        else:
            issuer = urlunparse(
                urlparse(request.url)._replace(path="", query="", fragment="")
            )

        if self.tokens is None:
            store = RefreshTokenStore()
            refresh_token = store.get_refresh_token_not_expired(issuer, TERRABYTE_CLIENT_ID)
            if refresh_token:
                try:
                    self.tokens = self.auth.get_tokens_from_refresh_token(
                        refresh_token=refresh_token
                    )
                except:
                    #toDo add logging infrastructure?
                    print("Token not valid")
                    refresh_token=None

                # TODO get access token from refresh_token
            if refresh_token is None:
                self.tokens = self.auth.get_tokens(True)
                if self.tokens.refresh_token:
                    store.set_refresh_token(
                        issuer,
                        TERRABYTE_CLIENT_ID,
                        self.tokens.refresh_token,
                    )

        request.headers["Authorization"] = f"Bearer {self.tokens.access_token}"
        return request


def create_requests_adapter(
    client_id: str = TERRABYTE_CLIENT_ID, issuer: str = TERRABYTE_AUTH_URL
):
    return RequestsAdapter(
        OidcDeviceAuthenticator(
            OidcClientInfo(
                client_id=client_id,
                provider=OidcProviderInfo(
                    issuer=issuer,
                ),
            ),
            use_pkce=True,
        )
    )


def wrap_request(session: requests.Session, url: str,client_id: str=TERRABYTE_CLIENT_ID, *args, **kwargs):
    session = requests.Session()
    request = requests.Request(url=url, *args, **kwargs)
    adapter = create_requests_adapter(
        client_id, TERRABYTE_AUTH_URL
    )
    request = adapter(request)
    prepped = session.prepare_request(request)
    return session.send(prepped)
