import os


TERRABYTE_AUTH_URL = os.environ.get(
    "TERRABYTE_AUTH_URL",
    "https://auth.terrabyte.lrz.de/realms/terrabyte/",
)
TERRABYTE_CLIENT_ID = os.environ.get(
    "TERRABYTE_CLIENT_ID",
    "at.eox.hub.terrabyte-api",
)
