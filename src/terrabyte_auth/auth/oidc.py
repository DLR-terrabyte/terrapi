import json
import base64
import enum
from typing import Any, Callable, Optional, Tuple, Union, List
from dataclasses import dataclass
import inspect
from urllib.parse import urljoin
import logging
import contextlib
import time
import hashlib
import random
import string

import requests

log = logging.getLogger(__name__)


class OidcException(Exception):
    pass


class OidcDeviceCodePollTimeout(OidcException):
    pass


def random_string(length=32, characters: str = None):
    """
    Build a random string from given characters (alphanumeric by default)
    """
    # TODO: move this to a utils module?
    characters = characters or (string.ascii_letters + string.digits)
    return "".join(random.choice(characters) for _ in range(length))


def create_timer() -> Callable[[], float]:
    """Create a timer function that returns elapsed time since creation of the timer function"""
    start = time.time()

    def elapsed():
        return time.time() - start

    return elapsed


@dataclass
class VerificationInfo:
    verification_uri: str
    verification_uri_complete: Optional[str]
    device_code: str
    user_code: str
    interval: int


def _like_print(display: Callable) -> Callable:
    """Ensure that display function supports an `end` argument like `print`"""
    if display is print or "end" in inspect.signature(display).parameters:
        return display
    else:
        return lambda *args, end="\n", **kwargs: display(*args, **kwargs)


def clip(x: float, min: float, max: float) -> float:
    """Clip given value between minimum and maximum value"""
    return min if x < min else (x if x < max else max)


class SimpleProgressBar:
    """Simple ASCII-based progress bar helper."""

    __slots__ = ["width", "bar", "fill", "left", "right"]

    def __init__(
        self,
        width: int = 40,
        *,
        bar: str = "#",
        fill: str = "-",
        left: str = "[",
        right: str = "]",
    ):
        self.width = int(width)
        self.bar = bar[0]
        self.fill = fill[0]
        self.left = left
        self.right = right

    def get(self, fraction: float) -> str:
        width = self.width - len(self.left) - len(self.right)
        bar = self.bar * int(round(width * clip(fraction, min=0, max=1)))
        return f"{self.left}{bar:{self.fill}<{width}s}{self.right}"


class _BasicDeviceCodePollUi:
    """
    Basic (print + carriage return) implementation of the device code
    polling loop UI (e.g. show progress bar and status).
    """

    def __init__(
        self,
        timeout: float,
        elapsed: Callable[[], float],
        max_width: int = 80,
        display: Callable = print,
    ):
        self.timeout = timeout
        self.elapsed = elapsed
        self._max_width = max_width
        self._status = "Authorization pending"
        self._display = _like_print(display)
        self._progress_bar = SimpleProgressBar(width=(max_width - 1) // 2)

    def _instructions(self, info: VerificationInfo) -> str:
        if info.verification_uri_complete:
            return f"Visit {info.verification_uri_complete} to authenticate."
        else:
            return f"Visit {info.verification_uri} and enter user code {info.user_code!r} to authenticate."

    def show_instructions(self, info: VerificationInfo) -> None:
        self._display(self._instructions(info=info))

    def set_status(self, status: str):
        self._status = status

    def show_progress(self, status: Optional[str] = None):
        if status:
            self.set_status(status)
        progress_bar = self._progress_bar.get(
            fraction=1.0 - self.elapsed() / self.timeout
        )
        text = f"{progress_bar} {self._status}"
        self._display(
            f"{text[:self._max_width]: <{self._max_width}s}", end="\r"
        )

    def close(self):
        self._display("", end="\n")


class _JupyterDeviceCodePollUi(_BasicDeviceCodePollUi):
    def __init__(
        self,
        timeout: float,
        elapsed: Callable[[], float],
        max_width: int = 80,
    ):
        super().__init__(timeout=timeout, elapsed=elapsed, max_width=max_width)
        import IPython.display

        self._instructions_display = IPython.display.display(
            {"text/html": " "}, raw=True, display_id=True
        )
        self._progress_display = IPython.display.display(
            {"text/html": " "}, raw=True, display_id=True
        )

    def _instructions(self, info: VerificationInfo) -> str:
        url = (
            info.verification_uri_complete
            if info.verification_uri_complete
            else info.verification_uri
        )
        instructions = f'Visit <a href="{url}" title="Authenticate at {url}" target="_blank" rel="noopener noreferrer">{url}</a>'
        instructions += f' <a href="#" onclick="navigator.clipboard.writeText({url!r});return false;" title="Copy authentication URL to clipboard">&#128203;</a>'
        if not info.verification_uri_complete:
            instructions += f" and enter user code {info.user_code!r}"
        instructions += " to authenticate."
        return instructions

    def show_instructions(self, info: VerificationInfo) -> None:
        self._instructions_display.update(
            {"text/html": self._instructions(info=info)}, raw=True
        )

    def show_progress(self, status: Optional[str] = None):
        # TODO Add emoticons to status?
        if status:
            self.set_status(status)
        progress_bar = self._progress_bar.get(
            fraction=1.0 - self.elapsed() / self.timeout
        )
        self._progress_display.update(
            {"text/html": f"<code>{progress_bar}</code> {self._status}"},
            raw=True,
        )

    def close(self):
        pass


def jwt_decode(token: str) -> Tuple[dict, dict]:
    """
    Poor man's JWT decoding
    TODO: use a real library that also handles verification properly?
    """

    def _decode(data: str) -> dict:
        decoded = base64.b64decode(data + "=" * (4 - len(data) % 4)).decode(
            "ascii"
        )
        return json.loads(decoded)

    header, payload, signature = token.split(".")
    return _decode(header), _decode(payload)


def in_jupyter_context() -> bool:
    """Check if we are running in an interactive Jupyter notebook context."""
    try:
        from ipykernel.zmqshell import ZMQInteractiveShell
        from IPython.core.getipython import get_ipython
    except ImportError:
        return False
    return isinstance(get_ipython(), ZMQInteractiveShell)


def url_join(root_url: str, path: str):
    """Join a base url and sub path properly."""
    return urljoin(root_url.rstrip("/") + "/", path.lstrip("/"))


class DefaultOidcClientGrant(enum.Enum):
    """
    Enum with possible values for "grant_types" field of default OIDC clients provided by backend.
    """
    IMPLICIT = "implicit"
    AUTH_CODE = "authorization_code"
    AUTH_CODE_PKCE = "authorization_code+pkce"
    DEVICE_CODE = "urn:ietf:params:oauth:grant-type:device_code"
    DEVICE_CODE_PKCE = "urn:ietf:params:oauth:grant-type:device_code+pkce"
    REFRESH_TOKEN = "refresh_token"


GrantsChecker = Union[List[DefaultOidcClientGrant], Callable[[List[DefaultOidcClientGrant]], bool]]


class OidcProviderInfo:
    """OpenID Connect Provider information, as provided by an openEO back-end (endpoint `/credentials/oidc`)"""

    def __init__(
        self,
        issuer: str = None,
        discovery_url: str = None,
        scopes: List[str] = None,
        provider_id: str = None,
        title: str = None,
        default_clients: Union[List[dict], None] = None,
        requests_session: Optional[requests.Session] = None,
    ):
        # TODO: id and title are required in the openEO API spec.
        self.id = provider_id
        self.title = title
        if discovery_url:
            self.discovery_url = discovery_url
        elif issuer:
            self.discovery_url = url_join(issuer, "/.well-known/openid-configuration")
        else:
            raise ValueError("At least `issuer` or `discovery_url` should be specified")
        if not requests_session:
            requests_session = requests.Session()
        discovery_resp = requests_session.get(self.discovery_url, timeout=20)
        discovery_resp.raise_for_status()
        self.config = discovery_resp.json()
        self.issuer = issuer or self.config["issuer"]
        # Minimal set of scopes to request
        self._supported_scopes = self.config.get("scopes_supported", ["openid"])
        self._scopes = {"openid"}.union(scopes or []).intersection(self._supported_scopes)
        log.debug(f"Scopes: provider supported {self._supported_scopes} & backend desired {scopes} -> {self._scopes}")
        self.default_clients = default_clients

    @classmethod
    def from_dict(cls, data: dict) -> "OidcProviderInfo":
        return cls(
            provider_id=data["id"], title=data["title"],
            issuer=data["issuer"],
            scopes=data.get("scopes"),
            default_clients=data.get("default_clients"),
        )

    def get_scopes_string(self, request_refresh_token: bool = False) -> str:
        """
        Build "scope" string for authentication request.

        :param request_refresh_token: include "offline_access" scope (if supported),
            which some OIDC providers require in order to return refresh token
        :return: space separated scope listing as single string
        """
        scopes = self._scopes
        if request_refresh_token and "offline_access" in self._supported_scopes:
            scopes = scopes | {"offline_access"}
        log.debug("Using scopes: {s}".format(s=scopes))
        return " ".join(sorted(scopes))

    def get_default_client_id(self, grant_check: GrantsChecker) -> Union[str, None]:
        """
        Get first default client that supports (as stated by provider's `grant_types`)
        the desired grant types (as implemented by `grant_check`)
        """
        if isinstance(grant_check, list):
            # Simple `grant_check` mode: just provide list of grants that all must be supported.
            desired_grants = grant_check
            grant_check = lambda grants: all(g in grants for g in desired_grants)

        def normalize_grants(grants: List[str]):
            for grant in grants:
                try:
                    yield DefaultOidcClientGrant(grant)
                except ValueError:
                    log.warning(f"Invalid OIDC grant type {grant!r}.")

        for client in self.default_clients or []:
            client_id = client.get("id")
            supported_grants = client.get("grant_types")
            supported_grants = list(normalize_grants(supported_grants))
            if client_id and supported_grants and grant_check(supported_grants):
                return client_id


class OidcClientInfo:
    """
    Simple container holding basic info of an OIDC client
    """

    def __init__(self, client_id: str, provider: OidcProviderInfo, client_secret: str = None):
        self.client_id = client_id
        self.provider = provider
        self.client_secret = client_secret
        # TODO: also info client type (desktop app, web app, SPA, ...)?

    # TODO: load from config file

    def guess_device_flow_pkce_support(self):
        """Best effort guess if PKCE should be used for device auth grant"""
        # Check if this client is also defined as default client with device_code+pkce
        default_clients = [c for c in self.provider.default_clients or [] if c["id"] == self.client_id]
        grant_types = set(g for c in default_clients for g in c.get("grant_types", []))
        return any("device_code+pkce" in g for g in grant_types)


@dataclass
class AccessTokenResult:
    """Container for result of access_token request."""

    access_token: str
    id_token: Optional[str] = None
    refresh_token: Optional[str] = None


class OidcAuthenticator:
    """
    Base class for OpenID Connect authentication flows.
    """
    grant_type = NotImplemented

    def __init__(
        self,
        client_info: OidcClientInfo,
        requests_session: Optional[requests.Session] = None,
    ):
        self._client_info = client_info
        self._provider_config = client_info.provider.config
        # TODO: check provider config (e.g. if grant type is supported)
        self._requests = requests_session or requests.Session()

    @property
    def client_info(self) -> OidcClientInfo:
        return self._client_info

    @property
    def client_id(self) -> str:
        return self._client_info.client_id

    @property
    def client_secret(self) -> str:
        return self._client_info.client_secret

    @property
    def provider_info(self) -> OidcProviderInfo:
        return self._client_info.provider

    def get_tokens(self, request_refresh_token: bool = False) -> AccessTokenResult:
        """Get access_token and possibly id_token+refresh_token."""
        result = self._do_token_post_request(post_data=self._get_token_endpoint_post_data())
        return self._get_access_token_result(result)

    def get_tokens_from_refresh_token(self, refresh_token: str):
        post_data = self._get_token_endpoint_post_data()
        post_data["grant_type"] = "refresh_token"
        post_data["refresh_token"] = refresh_token
        result = self._do_token_post_request(post_data)
        return self._get_access_token_result(result)

    def _get_token_endpoint_post_data(self) -> dict:
        """Build POST data dict to send to token endpoint"""
        return {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
        }

    def _do_token_post_request(self, post_data: dict) -> dict:
        """Do POST to token endpoint to get access token"""
        token_endpoint = self._provider_config['token_endpoint']
        log.info("Doing {g!r} token request {u!r} with post data fields {p!r} (client_id {c!r})".format(
            g=self.grant_type, c=self.client_id, u=token_endpoint, p=list(post_data.keys()))
        )
        resp = self._requests.post(url=token_endpoint, data=post_data)
        if resp.status_code != 200:
            # TODO: are other status_code values valid too?
            raise OidcException("Failed to retrieve access token at {u!r}: {s} {r!r} {t!r}".format(
                s=resp.status_code, r=resp.reason, u=resp.url, t=resp.text
            ))

        result = resp.json()
        log.debug("Token response with keys {k}".format(k=result.keys()))
        return result

    def _get_access_token_result(self, data: dict, expected_nonce: str = None) -> AccessTokenResult:
        """Parse JSON result from token request"""
        return AccessTokenResult(
            access_token=self._extract_token(data, "access_token"),
            id_token=self._extract_token(data, "id_token", expected_nonce=expected_nonce, allow_absent=True),
            refresh_token=self._extract_token(data, "refresh_token", allow_absent=True)
        )

    @staticmethod
    def _extract_token(data: dict, key: str, expected_nonce: str = None, allow_absent=False) -> Union[str, None]:
        """
        Extract token of given type ("access_token", "id_token", "refresh_token") from a token JSON response
        """
        try:
            token = data[key]
        except KeyError:
            if allow_absent:
                return
            raise OidcException("No {k!r} in response".format(k=key))
        if expected_nonce:
            # TODO: verify the JWT properly?
            _, payload = jwt_decode(token)
            if payload['nonce'] != expected_nonce:
                raise OidcException("Invalid nonce in {k}".format(k=key))
        return token


class PkceCode:
    """
    Simple container for PKCE code verifier and code challenge.

    PKCE, pronounced "pixy", is short for "Proof Key for Code Exchange".
    Also see https://tools.ietf.org/html/rfc7636
    """
    __slots__ = ["code_verifier", "code_challenge", "code_challenge_method"]

    def __init__(self):
        self.code_verifier = random_string(64)
        # Only SHA256 is supported for now.
        self.code_challenge_method = "S256"
        self.code_challenge = PkceCode.sha256_hash(self.code_verifier)

    @staticmethod
    def sha256_hash(code: str) -> str:
        """Apply SHA256 hash to code verifier to get code challenge"""
        data = hashlib.sha256(code.encode('ascii')).digest()
        return base64.urlsafe_b64encode(data).decode('ascii').replace('=', '')


class OidcDeviceAuthenticator(OidcAuthenticator):
    """
    Implementation of OAuth Device Authorization grant/flow
    """

    grant_type = "urn:ietf:params:oauth:grant-type:device_code"

    DEFAULT_MAX_POLL_TIME = 5 * 60

    def __init__(
        self,
        client_info: OidcClientInfo,
        display: Callable[[str], None] = print,
        device_code_url: Optional[str] = None,
        max_poll_time: float = DEFAULT_MAX_POLL_TIME,
        use_pkce: Optional[bool] = None,
        requests_session: Optional[requests.Session] = None,
    ):
        super().__init__(client_info=client_info, requests_session=requests_session)
        self._display = display
        # Allow to specify/override device code URL for cases when it is not available in OIDC discovery doc.
        self._device_code_url = device_code_url or self._provider_config.get("device_authorization_endpoint")
        if not self._device_code_url:
            raise OidcException("No support for device authorization grant")
        self._max_poll_time = max_poll_time
        if use_pkce is None:
            use_pkce = client_info.client_secret is None and client_info.guess_device_flow_pkce_support()
        self._pkce = PkceCode() if use_pkce else None

    def _get_verification_info(self, request_refresh_token: bool = False) -> VerificationInfo:
        """Get verification URL and user code"""
        post_data = {
            "client_id": self.client_id,
            # "client_secret": self.client_secret,
            "scope": self._client_info.provider.get_scopes_string(request_refresh_token=request_refresh_token)
        }
        if self._pkce:
            post_data["code_challenge"] = self._pkce.code_challenge,
            post_data["code_challenge_method"] = self._pkce.code_challenge_method
        resp = self._requests.post(url=self._device_code_url, data=post_data)
        if resp.status_code != 200:
            raise OidcException("Failed to get verification URL and user code from {u!r}: {s} {r!r} {t!r}".format(
                s=resp.status_code, r=resp.reason, u=resp.url, t=resp.text
            ))
        try:
            data = resp.json()
            verification_info = VerificationInfo(
                # Google OAuth/OIDC implementation uses non standard "verification_url" instead of "verification_uri"
                verification_uri=data["verification_uri"] if "verification_uri" in data else data["verification_url"],
                # verification_uri_complete is optional, will be None if this key is not present
                verification_uri_complete=data.get("verification_uri_complete"),
                device_code=data["device_code"],
                user_code=data["user_code"],
                interval=data.get("interval", 5),
            )
        except Exception as e:
            raise OidcException("Failed to parse device authorization request: {e!r}".format(e=e))
        log.debug("Verification info: %r", verification_info)
        return verification_info

    def get_tokens(self, request_refresh_token: bool = False, refresh_token: str = None) -> AccessTokenResult:
        # Get verification url and user code
        verification_info = self._get_verification_info(request_refresh_token=request_refresh_token)

        # Poll token endpoint
        token_endpoint = self._provider_config['token_endpoint']
        post_data = {
            "client_id": self.client_id,
            "device_code": verification_info.device_code,
            "grant_type": self.grant_type
        }

        if refresh_token is not None:
            print("Using refres token")
            post_data["refresh_token"] = refresh_token

        if self._pkce:
            post_data["code_verifier"] = self._pkce.code_verifier
        else:
            post_data["client_secret"] = self.client_secret

        poll_interval = verification_info.interval
        log.debug("Start polling token endpoint (interval {i}s)".format(i=poll_interval))

        elapsed = create_timer()
        next_poll = elapsed() + poll_interval
        # TODO: let poll UI determine sleep interval?
        sleep = clip(self._max_poll_time / 100, min=1, max=5)

        if in_jupyter_context():
            poll_ui = _JupyterDeviceCodePollUi(timeout=self._max_poll_time, elapsed=elapsed)
        else:
            poll_ui = _BasicDeviceCodePollUi(timeout=self._max_poll_time, elapsed=elapsed, display=self._display)
        poll_ui.show_instructions(info=verification_info)

        with contextlib.closing(poll_ui):
            while elapsed() <= self._max_poll_time:
                poll_ui.show_progress()
                time.sleep(sleep)

                if elapsed() >= next_poll:
                    log.debug(
                        f"Doing {self.grant_type!r} token request {token_endpoint!r} with post data fields {list(post_data.keys())!r} (client_id {self.client_id!r})"
                    )
                    poll_ui.show_progress(status="Polling")
                    resp = self._requests.post(url=token_endpoint, data=post_data, timeout=5)
                    if resp.status_code == 200:
                        log.info(f"[{elapsed():5.1f}s] Authorized successfully.")
                        poll_ui.show_progress(status="Authorized successfully")
                        # TODO remove progress bar when authorized succesfully?
                        return self._get_access_token_result(data=resp.json())
                    else:
                        try:
                            error = resp.json()["error"]
                        except Exception:
                            error = "unknown"
                        log.info(f"[{elapsed():5.1f}s] not authorized yet: {error}")
                        if error == "authorization_pending":
                            poll_ui.show_progress(status="Authorization pending")
                        elif error == "slow_down":
                            poll_ui.show_progress(status="Slowing down")
                            poll_interval += 5
                        else:
                            # TODO: skip occasional glitches (e.g. see `SkipIntermittentFailures` from openeo-aggregator)
                            raise OidcException(
                                f"Failed to retrieve access token at {token_endpoint!r}: {resp.status_code} {resp.reason!r} {resp.text!r}"
                            )
                    next_poll = elapsed() + poll_interval

            poll_ui.show_progress(status="Timed out")
            raise OidcDeviceCodePollTimeout(f"Timeout ({self._max_poll_time:.1f}s) while polling for access token.")
