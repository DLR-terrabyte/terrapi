import os


TERRABYTE_PUBLIC_API_URL = os.environ.get(
    "TERRABYTE_PUBLIC_API_URL",
    # "https://gateway.terrabyte.eox.at/public/stac",
    #"https://terrabyte-api.hub.eox.at/public/stac"
    "https://stac.terrabyte.lrz.de/public/api"

)
TERRABYTE_PRIVATE_API_URL = os.environ.get(
    "TERRABYTE_PRIVATE_API_URL",
    # "https://gateway.terrabyte.eox.at/private/stac",
    #"https://terrabyte-api.hub.eox.at/private/stac"
    "https://stac.terrabyte.lrz.de/private/api"
)

TERRABYTE_AUTH_URL = os.environ.get(
    "TERRABYTE_AUTH_URL",
    "https://auth.terrabyte.lrz.de/realms/terrabyte/",
)

TERRABYTE_CLIENT_ID = os.environ.get(
    "TERRABYTE_CLIENT_ID",
    "at.eox.hub.terrabyte-api",
   # "de.lrz.terrabyte.stac"
)
