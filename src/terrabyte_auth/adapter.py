
from typing import Optional

import requests

from .auth.config import RefreshTokenStore
from .auth.oidc import (
    OidcDeviceAuthenticator,
    AccessTokenResult,
    OidcClientInfo,
    OidcProviderInfo,
)

from .settings import TERRABYTE_AUTH_URL, TERRABYTE_PRIVATE_API_URL, TERRABYTE_CLIENT_ID


class RequestsAdapter:
    tokens: Optional[AccessTokenResult]

    def __init__(self, auth: OidcDeviceAuthenticator):
        self.auth = auth
        self.tokens = None

    def __call__(self, request: requests.Request) -> Optional[requests.Request]:
        if self.tokens is None:
            store = RefreshTokenStore()
            refresh_token = store.get_refresh_token(TERRABYTE_PRIVATE_API_URL, TERRABYTE_CLIENT_ID)
            if refresh_token:
                print(refresh_token)
                self.tokens = self.auth.get_tokens_from_refresh_token(refresh_token=refresh_token)
                # TODO get access token from refresh_token
            else:
                print("requesting token")
                self.tokens = self.auth.get_tokens(True)
                if self.tokens.refresh_token:
                    store.set_refresh_token(
                        TERRABYTE_PRIVATE_API_URL,
                        TERRABYTE_CLIENT_ID,
                        self.tokens.refresh_token,
                    )

        # auth_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5U0ZVZHZWM2FrZXdpbzVYb1dhMThxci16eVdzZWszMjNOQkxUNnZ2Q1dFIn0.eyJleHAiOjE2OTc2MzMyNzUsImlhdCI6MTY5NzYzMjk3NSwiYXV0aF90aW1lIjoxNjk3NjMyOTY5LCJqdGkiOiJlN2YwMTk0OS05NzYyLTQwZmItYjg3MS03YjUyMzdhNWRlOTIiLCJpc3MiOiJodHRwczovL2F1dGgudGVycmFieXRlLmxyei5kZS9yZWFsbXMvdGVycmFieXRlIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjhhMWJiYmRhLWMzYzQtNDJlZC1iZGE5LWFkZjZiNWY1YmI3MCIsInR5cCI6IkJlYXJlciIsImF6cCI6ImF0LmVveC5odWIudGVycmFieXRlLWFwaSIsInNlc3Npb25fc3RhdGUiOiIwMmJlYzM5Ny00NWQzLTQ5YjMtYThiNC1kYTQyYjU2NWY1OGYiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vdGVycmFieXRlLWFwaS5odWIuZW94LmF0LyIsImh0dHBzOi8vdGVycmFieXRlLWFwaS5odWIuZW94LmF0Il0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXRlcnJhYnl0ZSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiMDJiZWMzOTctNDVkMy00OWIzLWE4YjQtZGE0MmI1NjVmNThmIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiRmFiaWFuIFNjaGluZGxlciIsImdyb3VwcyI6WyIvZHNzL3BuNTZzdS1kc3MtMDAwMC1ybyIsIi9kc3MvcG41NnN1LWRzcy0wMDE5Il0sInByZWZlcnJlZF91c2VybmFtZSI6ImRpOTNiYWIiLCJnaXZlbl9uYW1lIjoiRmFiaWFuIiwiZmFtaWx5X25hbWUiOiJTY2hpbmRsZXIiLCJlbWFpbCI6ImZhYmlhbi5zY2hpbmRsZXJAZW94LmF0In0.G_79jt_MJjgirlEXZH3N7dQ1xH_UFOLcgVIBfI-4yUq8g74WrZ2OZF8TxVNkr7Bpb5WTi2LOtr69i1l2TYTsXGwWadUjU4VJS-UuZpptCwCdwz4d08nlfy5Vot1PvMY0vUbK3RGr5_hnZLVp3KlHWA9qQKQ60iyg8wbtNO0cHz5LQiiIaVQaTuodgOHx3ja9yJwxZMo5vKze4D77aNPvIZ5ZjJ5yi0ivS6pedvR2D50WUfDdcwleEUrW0YKiqij3iVGy5W_XFXsM54lsxwTphVDPs0-tVv2ofiZTjUTvTv1-xaz3ZcYkpWEsAY6ByrB9vcrzgJn9aUYxR-QtQmTUAw"
        # id_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5U0ZVZHZWM2FrZXdpbzVYb1dhMThxci16eVdzZWszMjNOQkxUNnZ2Q1dFIn0.eyJleHAiOjE2OTc2MzMyNzUsImlhdCI6MTY5NzYzMjk3NSwiYXV0aF90aW1lIjoxNjk3NjMyOTY5LCJqdGkiOiIzMmE5MjM0NC1mOGNiLTQxNmUtYjQ3Ny0zZDUxYmM4Yzg2NWEiLCJpc3MiOiJodHRwczovL2F1dGgudGVycmFieXRlLmxyei5kZS9yZWFsbXMvdGVycmFieXRlIiwiYXVkIjoiYXQuZW94Lmh1Yi50ZXJyYWJ5dGUtYXBpIiwic3ViIjoiOGExYmJiZGEtYzNjNC00MmVkLWJkYTktYWRmNmI1ZjViYjcwIiwidHlwIjoiSUQiLCJhenAiOiJhdC5lb3guaHViLnRlcnJhYnl0ZS1hcGkiLCJzZXNzaW9uX3N0YXRlIjoiMDJiZWMzOTctNDVkMy00OWIzLWE4YjQtZGE0MmI1NjVmNThmIiwiYXRfaGFzaCI6ImlQakJGRGdUU1lzbzBzTlZRczBhQkEiLCJhY3IiOiIxIiwic2lkIjoiMDJiZWMzOTctNDVkMy00OWIzLWE4YjQtZGE0MmI1NjVmNThmIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiRmFiaWFuIFNjaGluZGxlciIsImdyb3VwcyI6WyIvZHNzL3BuNTZzdS1kc3MtMDAwMC1ybyIsIi9kc3MvcG41NnN1LWRzcy0wMDE5Il0sInByZWZlcnJlZF91c2VybmFtZSI6ImRpOTNiYWIiLCJnaXZlbl9uYW1lIjoiRmFiaWFuIiwiZmFtaWx5X25hbWUiOiJTY2hpbmRsZXIiLCJlbWFpbCI6ImZhYmlhbi5zY2hpbmRsZXJAZW94LmF0In0.hjI5b8UCaLkccT60KZqu5cs9J65Ie1Lvuc1ZJhqljsjaM_WTRrenqkzrDrRrELpGoe3_zHFsdOUt_bfEL7V8UA1z9Nyeqha2_qWxCKk0n7cwbwUgy0h3umZvdLf1_QVV8GJ0Jrm6p4M7bTzTm9QvfOMdCOQmsU1hkr_v7od6gcWB7VF7jaij6_swfr3D4sFrrZAmcNOdhem9lZcAaa5HKbSXHweJ-bKHCylfuqH5D1qlRLoRK7eTUQaE0WLkYsU0c99Z_Q1moKKBGhmRATEftEFeh1rM3QcDpQE-5UKloXBJ0amrDvfyDWDnp7exmaDNo3REkWBbwrB9JJBiQx2PjA"

        request.headers["Authorization"] = f"Bearer {self.tokens.access_token}"
        # request.headers["Authorization"] = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ5U0ZVZHZWM2FrZXdpbzVYb1dhMThxci16eVdzZWszMjNOQkxUNnZ2Q1dFIn0.eyJleHAiOjE3MDU1MjYzNDksImlhdCI6MTcwNTUyNjA0OSwiYXV0aF90aW1lIjoxNzA1NTI2MDQ1LCJqdGkiOiIzOWVkZjczMC03Y2ViLTQxZTUtYjYzYS02ZWMzNmI4MWNkYmEiLCJpc3MiOiJodHRwczovL2F1dGgudGVycmFieXRlLmxyei5kZS9yZWFsbXMvdGVycmFieXRlIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjhhMWJiYmRhLWMzYzQtNDJlZC1iZGE5LWFkZjZiNWY1YmI3MCIsInR5cCI6IkJlYXJlciIsImF6cCI6ImF0LmVveC5odWIudGVycmFieXRlLWFwaSIsInNlc3Npb25fc3RhdGUiOiJhYzdhMDBmZS04MjQ5LTRkODQtOWYzMi1kNGM1NTU1ZDA3M2EiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHBzOi8vdGVycmFieXRlLWFwaS5odWIuZW94LmF0LyIsImh0dHBzOi8vdGVycmFieXRlLWFwaS5odWIuZW94LmF0Il0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJkZWZhdWx0LXJvbGVzLXRlcnJhYnl0ZSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwic2lkIjoiYWM3YTAwZmUtODI0OS00ZDg0LTlmMzItZDRjNTU1NWQwNzNhIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJuYW1lIjoiRmFiaWFuIFNjaGluZGxlciIsImdyb3VwcyI6WyIvZHNzL3BuNTZzdS1kc3MtMDAwMC1ybyIsIi9kc3MvcG41NnN1LWRzcy0wMDE5Il0sInByZWZlcnJlZF91c2VybmFtZSI6ImRpOTNiYWIiLCJnaXZlbl9uYW1lIjoiRmFiaWFuIiwiZmFtaWx5X25hbWUiOiJTY2hpbmRsZXIiLCJlbWFpbCI6ImZhYmlhbi5zY2hpbmRsZXJAZW94LmF0In0.Y--8bc1YRb6P2KgePhTvlGl7Q51Xp9BYaXLMsrrfRKGSdPwC6cba50SbvWhXOKr_JWn_yUfwPk2epJACl3ZaQHelEY2VJKZ-ArlRPAx0BpNHBusDQpOhecEhqNP1XWx3c3xEr3yQakrLkhKTKGmf56fQWVW9pZGCzRgEuqEufP9dQCbu0tA8KxOHmxYxpmeqlAcWaUD-nxIwTI5UyR8welaxeedCdPsnfBvDrjONYE8RDy4dTSXVH3lO6AFWLE6nTs0skUlhJuY1eASBUHynY8kVUqXI_uI7r-ZpAc54oPcY4WMfitbEJUyRCZzJRzqy9f_Qb75yyQfBGKA0PGAfsg"
        print(self.tokens.access_token)
        print(self.tokens.refresh_token)
        return request


def create_requests_adapter(client_id: str=TERRABYTE_CLIENT_ID, issuer: str=TERRABYTE_AUTH_URL):
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