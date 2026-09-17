from typing import Optional
from urllib.parse import urlparse, urlunparse
import datetime

import requests
import click

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
        self._last_token_time = None

    def _get_tokens(self, force_renew: bool = False, not_expired_before: Optional[datetime.datetime] = None, issuer: Optional[str] = None) -> AccessTokenResult:
        """Get access tokens, either from cache or by performing a new login.
        Tokens are reused for up to 2 minutes to prevent expired tokens in long-running scripts.
        """
        # Use provided issuer, then self.issuer, then default
        issuer = issuer or self.issuer or TERRABYTE_AUTH_URL
        
        # Check if the token is older than 2 minutes
        now = datetime.datetime.now()
        if self.tokens is not None and self._last_token_time is not None and not force_renew:
            if (now - self._last_token_time) < datetime.timedelta(minutes=2):
                return self.tokens

        if force_renew or self.tokens is None:
            store = RefreshTokenStore()
            refresh_token = store.get_refresh_token_not_expired(issuer, TERRABYTE_CLIENT_ID)
        else:
            refresh_token = self.tokens.refresh_token
            
        if refresh_token:
            try:
                self.tokens = self.auth.get_tokens_from_refresh_token(
                    refresh_token=refresh_token
                )
                self._last_token_time = datetime.datetime.now()
            except Exception as e:
                click.echo(f"Token refresh failed: {e}", err=True)
                refresh_token = None

        if refresh_token is None or force_renew:
            self.tokens = self.auth.get_tokens(True, not_expired_before=not_expired_before)
            self._last_token_time = datetime.datetime.now()
            if self.tokens.refresh_token:
                store.set_refresh_token(
                    issuer,
                    TERRABYTE_CLIENT_ID,
                    self.tokens.refresh_token,
                )
        
        return self.tokens


    def __call__(self, request: requests.Request) -> Optional[requests.Request]:
        issuer = self.issuer
        if not issuer:
            issuer = urlunparse(
                urlparse(request.url)._replace(path="", query="", fragment="")
            )

        # Ensure tokens are loaded for this specific issuer
        self._get_tokens(issuer=issuer)

        request.headers["Authorization"] = f"Bearer {self.tokens.access_token}"
        return request


def create_requests_adapter(
    client_id: str = TERRABYTE_CLIENT_ID, issuer: str = TERRABYTE_AUTH_URL
)->RequestsAdapter:
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


def wrap_request(
    session: Optional[requests.Session], 
    url: str, 
    client_id: str = TERRABYTE_CLIENT_ID, 
    adapter: Optional[RequestsAdapter] = None,
    *args, 
    **kwargs
) -> requests.Response:
    """Wraps a request with authentication and optional session sharing.
    
    If no session is provided, a new one is created.
    If no adapter is provided, a new one is created using client_id.
    """
    if session is None:
        session = requests.Session()
    
    request = requests.Request(url=url, *args, **kwargs)
    
    if adapter is None:
        adapter = create_requests_adapter(client_id, TERRABYTE_AUTH_URL)
    
    request = adapter(request)
    prepped = session.prepare_request(request)
    return session.send(prepped)
