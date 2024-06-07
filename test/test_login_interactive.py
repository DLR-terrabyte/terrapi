import sys
import os
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
#from click.testing import CliRunner
import terrabyte_auth.stac_api_cli 
from datetime import datetime, timezone, timedelta


#TerrApiStac(["login", "-h "])
#TerrApiStac(["login"])
#TerrApiStac(["-h"])
#runner = CliRunner()
#result = runner.invoke(stacApiCli, ['login','--help'])
#print(result.stdout_bytes)
terrabyte_auth.stac_api_cli.debugCli = True

collection_json_str = '{"id": "di39rer.terrapi3", "type": "Collection", "links": [{"rel": "items", "type": "application/geo+json", "href": "https://stac.terrabyte.lrz.de/private/api/collections/di39rer.terrapi1/items"}, {"rel": "parent", "type": "application/json", "href": "https://stac.terrabyte.lrz.de/private/api/"}, {"rel": "root", "type": "application/json", "href": "https://stac.terrabyte.lrz.de/private/api/"}, {"rel": "self", "type": "application/json", "href": "https://stac.terrabyte.lrz.de/private/api/collections/di39rer.terrapi1"}], "title": "Private User di39rer Test Collection", "extent": {"spatial": {"bbox": [[-180, -90.18, 90]]}, "temporal": {"interval": [[null, null]]}}, "license": "proprietary", "description": "Test Collection for terraApi tests", "stac_version": "1.0.0"}'

item_json_str = '{"type": "Feature", "stac_version": "1.0.0", "id": "test_item", "properties": {"datetime": "2024-05-10T15:53:16.721125Z"}, "geometry": {"type": "Point", "coordinates": [0, 0]}, "links": [], "assets": {}, "stac_extensions": []}'


if __name__ == '__main__':
    terrabyte_auth.stac_api_cli.login.callback(delete=True)
    terrabyte_auth.stac_api_cli.login.callback(valid=True)
    terrabyte_auth.stac_api_cli.login.callback()
    #terrabyte_auth.stac_api_cli.login.callback(valid=True)
   # print("Test: Create Item")
    #terrabyte_auth.stac_api_cli.list_item.callback("di39rer.terrapi4")
    #print("Test: create Collection")
    #terrabyte_auth.stac_api_cli.create.callback()
    #terrabyte_auth.stac_api_cli.create.callback()
    #print("Trying to create Collection of other user")
    #stac_cmd(["--debug","collection","create","--id","di93bor.terror","-u" ,"-j", collection_json_str])
   
    
    if False:

        print("Test: Login via Browser URL")
        terrabyte_auth.stac_api_cli.login.callback()

        print("Test: Print how long Token is Valid")
        terrabyte_auth.stac_api_cli.login.callback(valid=True)

        print("Test: Deleting Refresh Token")
        terrabyte_auth.stac_api_cli.login.callback(delete=True)
        
        print("Test: Print how long Token is Valid, none should exist")
        terrabyte_auth.stac_api_cli.login.callback(valid=True)
        
        print("Test: Login via Browser URL")
        terrabyte_auth.stac_api_cli.login.callback()
        
        print("Test: Print how long Token is Valid")
        terrabyte_auth.stac_api_cli.login.callback(valid=True)
        
        print("Test: Checking if it is valid for 10 hours")
        terrabyte_auth.stac_api_cli.login.callback(hours=10)
        
        print("Test: Checking if it is valid for 2 days ")
        terrabyte_auth.stac_api_cli.login.callback(days=2)

        date_till=datetime.now()+timedelta(days=1,hours=4,minutes=7)
        print(f"Test: Checking if it is valid till {date_till} ")
        terrabyte_auth.stac_api_cli.login.callback(till=date_till)
        
        print("Test: Checking if it is valid for 20 days, this should force new login ")
        terrabyte_auth.stac_api_cli.login.callback(days=20)

        print("Test: Forcing relogin")
        terrabyte_auth.stac_api_cli.login.callback(force=True)



