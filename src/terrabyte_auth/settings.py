import os

TERRABYTE_PUBLIC_API_URL = os.environ.get(
    "TERRABYTE_PUBLIC_API_URL",
    "https://stac.terrabyte.lrz.de/public/api"
)

TERRABYTE_PRIVATE_API_URL = os.environ.get(
    "TERRABYTE_PRIVATE_API_URL",
    "https://stac.terrabyte.lrz.de/private/api"
)

TERRABYTE_RESTRICTED_DATA_API_URL = os.environ.get(
    "TERRABYTE_RESTRICTED_DATA_API_URL",
    "https://stac.terrabyte.lrz.de/restricted-data"
)



TERRABYTE_AUTH_URL = os.environ.get(
    "TERRABYTE_AUTH_URL",
    "https://auth.terrabyte.lrz.de/realms/terrabyte/",
)

TERRABYTE_CLIENT_ID = os.environ.get(
    "TERRABYTE_CLIENT_ID",
    "de.lrz.terrabyte.stac"
)
