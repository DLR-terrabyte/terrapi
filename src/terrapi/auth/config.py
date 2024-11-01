# The functions within this file were originally copied from the repository 'https://github.com/Open-EO/openeo-python-client/blob/v0.28.0/openeo/rest/auth/config.py'
# provided under the Apache License 2.0.

"""
Functionality to store and retrieve authentication settings (usernames, passwords, client ids, ...)
from local config files.
"""

# TODO: also allow to set client_id, client_secret, refresh_token through env variables?


import json
import logging
import platform
import stat
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Tuple, Union

import jwt

from .. import __version__
from ..config import get_user_config_dir, get_user_data_dir
from ..util import deep_get, deep_set, rfc3339

try:
    # Use oschmod when available (fall back to POSIX-only functionality from stdlib otherwise)
    # TODO: enforce oschmod as dependency for all platforms?
    import oschmod
except ImportError:
    oschmod = None


_PRIVATE_PERMS = stat.S_IRUSR | stat.S_IWUSR

log = logging.getLogger(__name__)


def get_file_mode(path: Path) -> int:
    """Get the file permission bits in a way that works on both *nix and Windows platforms."""
    if oschmod:
        return oschmod.get_mode(str(path))
    return path.stat().st_mode


def set_file_mode(path: Path, mode: int):
    """Set the file permission bits in a way that works on both *nix and Windows platforms."""
    if oschmod:
        oschmod.set_mode(str(path), mode=mode)
    else:
        path.chmod(mode=mode)


def assert_private_file(path: Path):
    """Check that given file is only readable by user."""
    mode = get_file_mode(path)
    if (mode & stat.S_IRWXG) or (mode & stat.S_IRWXO):
        message = "File {p} could be readable by others: mode {a:o} (expected: {e:o}).".format(
            p=path, a=mode & (stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO), e=_PRIVATE_PERMS
        )
        if platform.system() == "Windows":
            log.info(message)
        else:
            raise PermissionError(message)


def utcnow_rfc3339() -> str:
    """Current datetime formatted as RFC-3339 string."""
    return rfc3339.datetime(datetime.utcnow())


def _normalize_url(url: str) -> str:
    """Normalize a url (trim trailing slash), to simplify equality checking."""
    return url.rstrip("/") or "/"


class PrivateJsonFile:
    """
    Base class for private config/data files in JSON format.
    """

    DEFAULT_FILENAME = "private.json"

    def __init__(self, path: Path = None):
        if path is None:
            path = self.default_path()
        if path.is_dir():
            path = path / self.DEFAULT_FILENAME
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    @classmethod
    def default_path(cls) -> Path:
        return get_user_config_dir(auto_create=True) / cls.DEFAULT_FILENAME

    def load(self, empty_on_file_not_found=True) -> dict:
        """Load all data from file"""
        if not self._path.exists():
            if empty_on_file_not_found:
                return {}
            raise FileNotFoundError(self._path)
        assert_private_file(self._path)
        log.debug("Loading private JSON file {p}".format(p=self._path))
        # TODO: add file locking to avoid race conditions?
        with self._path.open("r", encoding="utf8") as f:
            return json.load(f)

    def _write(self, data: dict):
        """Write whole data to file."""
        log.debug("Writing private JSON file {p}".format(p=self._path))
        # TODO: add file locking to avoid race conditions?
        with self._path.open("w", encoding="utf8") as f:
            json.dump(data, f, indent=2)
        set_file_mode(self._path, mode=_PRIVATE_PERMS)
        assert_private_file(self._path)

    def get(self, *keys, default=None) -> Union[dict, str, int]:
        """Load JSON file and do deep get with given keys."""
        result = deep_get(self.load(), *keys, default=default)
        if isinstance(result, Exception) or (isinstance(result, type) and issubclass(result, Exception)):
            # pylint: disable=raising-bad-type
            raise result
        return result

    def set(self, *keys, value):
        data = self.load()
        deep_set(data, *keys, value=value)
        self._write(data)

    def remove(self):
        if self._path.exists():
            log.debug(f"Removing {self._path}")
            self._path.unlink()


class AuthConfig(PrivateJsonFile):
    DEFAULT_FILENAME = "auth-config.json"

    @classmethod
    def default_path(cls) -> Path:
        return get_user_config_dir(auto_create=True) / cls.DEFAULT_FILENAME

    def _write(self, data: dict):
        # When starting fresh: add some metadata and defaults
        if "metadata" not in data:
            data["metadata"] = {
                "type": "AuthConfig",
                "created": utcnow_rfc3339(),
                "created_by": "openeo-python-client {v}".format(v=__version__),
                "version": 1,
            }
            data.setdefault("general", {})
            data.setdefault("backends", {})
        return super()._write(data=data)

    def get_basic_auth(self, backend: str) -> Tuple[Union[None, str], Union[None, str]]:
        """Get username/password combo for given backend. Values will be None when no config is available."""
        basic = self.get("backends", _normalize_url(backend), "basic", default={})
        username = basic.get("username")
        password = basic.get("password") if username else None
        return username, password

    def set_basic_auth(self, backend: str, username: str, password: Union[str, None]):
        data = self.load()
        keys = ("backends", _normalize_url(backend), "basic",)
        # TODO: support multiple basic auth credentials? (pick latest by default for example)
        deep_set(data, *keys, "date", value=utcnow_rfc3339())
        deep_set(data, *keys, "username", value=username)
        if password:
            deep_set(data, *keys, "password", value=password)
        self._write(data)

    def get_oidc_provider_configs(self, backend: str) -> Dict[str, dict]:
        """
        Get provider config items for given backend.

        Returns a dict mapping provider_id to dicts with "client_id" and "client_secret" items
        """
        return self.get("backends", _normalize_url(backend), "oidc", "providers", default={})

    def get_oidc_client_configs(self, backend: str, provider_id: str) -> Tuple[str, str]:
        """
        Get client_id and client_secret for given backend+provider_id. Values will be None when no config is available.
        """
        client = self.get("backends", _normalize_url(backend), "oidc", "providers", provider_id, default={})
        client_id = client.get("client_id")
        client_secret = client.get("client_secret") if client_id else None
        return client_id, client_secret

    def set_oidc_client_config(
            self, backend: str, provider_id: str,
            client_id: Union[str, None], client_secret: Union[str, None] = None, issuer: Union[str, None] = None
    ):
        data = self.load()
        keys = ("backends", _normalize_url(backend), "oidc", "providers", provider_id)
        # TODO: support multiple clients? (pick latest by default for example)
        deep_set(data, *keys, "date", value=utcnow_rfc3339())
        deep_set(data, *keys, "client_id", value=client_id)
        deep_set(data, *keys, "client_secret", value=client_secret)
        if issuer:
            deep_set(data, *keys, "issuer", value=issuer)
        self._write(data)


class RefreshTokenStore(PrivateJsonFile):
    """
    Basic JSON-file based storage of refresh tokens.
    """

    DEFAULT_FILENAME = "refresh-tokens.json"

    @classmethod
    def default_path(cls) -> Path:
        return get_user_data_dir(auto_create=True) / cls.DEFAULT_FILENAME

    def get_refresh_token(self, issuer: str, client_id: str) -> Union[str, None]:
        return self.get(_normalize_url(issuer), client_id, "refresh_token", default=None)
    
    def get_refresh_token_not_expired(self, issuer: str, client_id: str, than: datetime= datetime.now()) -> Union[str, None]:
        if than.tzinfo is None:
            than = than.replace(tzinfo=timezone.utc)

        token = self.get_refresh_token(issuer, client_id)
        if token is None:
            return None

        decoded = jwt.decode(token, options={"verify_signature": False})
        logging.info(f"jwt decoded: {decoded}")
        try: 
            iat = datetime.fromtimestamp(decoded["exp"], timezone.utc)
        except Exception:
            logging.info(f"Failed to access exp Field in decoded refresh token. Decoded result was: {decoded} ")
        
        if iat < than:
            self.delete_refresh_token(issuer, client_id)
            return None
        return token
    

    def set_refresh_token(self, issuer: str, client_id: str, refresh_token: str):
        data = self.load()
        log.info("Storing refresh token for issuer {i!r} (client {c!r})".format(i=issuer, c=client_id))
        deep_set(data, _normalize_url(issuer), client_id, value={
            "date": utcnow_rfc3339(),
            "refresh_token": refresh_token,
        })
        self._write(data)

    def delete_refresh_token(self, issuer: str, client_id: str):
        data = self.load()
        log.info("Deleting refresh token for issuer {i!r} (client {c!r})".format(i=issuer, c=client_id))
        issuer_info: dict = data.get(_normalize_url(issuer), {})
        issuer_info.pop(client_id, None)
        self._write(data)

    def delete_if_issued_at_older(self, issuer: str, client_id: str, than: datetime) -> bool:
        if than.tzinfo is None:
            than = than.replace(tzinfo=timezone.utc)

        token = self.get_refresh_token(issuer, client_id)
        if token is None:
            return False

        decoded = jwt.decode(token, options={"verify_signature": False})
        iat = datetime.fromtimestamp(decoded["iat"], timezone.utc)
        if iat < than:
            self.delete_refresh_token(issuer, client_id)
            return True
        return False
    
    def get_expiry_date_refresh_token(self, issuer: str, client_id: str, debug:bool = False)-> Union[datetime, None]:
        token = self.get_refresh_token(issuer, client_id)
        if token is None:
            return None
        decoded = jwt.decode(token, options={"verify_signature": False})
        if debug: print(decoded)
        return datetime.fromtimestamp(decoded["exp"], timezone.utc)

    def delete_if_expires_sooner(self, issuer: str, client_id: str, than: datetime) -> bool:
        if than.tzinfo is None:
            than = than.replace(tzinfo=timezone.utc)

        token = self.get_refresh_token(issuer, client_id)
        if token is None:
            return False

        decoded = jwt.decode(token, options={"verify_signature": False})
    
        iat = datetime.fromtimestamp(decoded["exp"], timezone.utc)
        if iat < than:
            self.delete_refresh_token(issuer, client_id)
            return True
        return False
