import sys
import os
import json
import ast
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import click
from click.testing import CliRunner
import terrapi.stac_api_cli 
import terrapi.terrapi_cli

runner = CliRunner()

#checks to run
checkLogin = False
checkauth = True
checkCollection = False
checkItem = False
checkHelp = False
checkPublic = False
checkErrorCode = False
checkPrefix = False



def stac_cmd(args:list ,out_str_assert:list =None):
    #print("running cmd ")
    runner = CliRunner()
    result = runner.invoke(terrapi.stac_api_cli.stac, args)
    #print("done")
    click.echo(result.stdout)
    click.echo("------")
    #click.echo("   ")
    assert result.exit_code == 0
    if out_str_assert is not None:
        for str in out_str_assert:
            assert str in result.output
    

def terrapi_cmd(args:list ,out_str_assert:list =None):
    runner = CliRunner()
    result = runner.invoke(terrapi.terrapi_cli.terrapi , args)
    click.echo(result.stdout)
    click.echo("------")
    click.echo("   ")
    assert result.exit_code == 0
    if out_str_assert is not None:
        for str in out_str_assert:
            assert str in result.output
    

collection_json_str = '{"id": "di39rer.terrapi3", "type": "Collection", "links": [{"rel": "items", "type": "application/geo+json", "href": "https://stac.terrabyte.lrz.de/private/api/collections/di39rer.terrapi1/items"}, {"rel": "parent", "type": "application/json", "href": "https://stac.terrabyte.lrz.de/private/api/"}, {"rel": "root", "type": "application/json", "href": "https://stac.terrabyte.lrz.de/private/api/"}, {"rel": "self", "type": "application/json", "href": "https://stac.terrabyte.lrz.de/private/api/collections/di39rer.terrapi1"}], "title": "Private User di39rer Test Collection", "extent": {"spatial": {"bbox": [[-180, -90.18, 90]]}, "temporal": {"interval": [[null, null]]}}, "license": "proprietary", "description": "Test Collection for terraApi tests", "stac_version": "1.0.0"}'

item_json_str = '{"type": "Feature", "stac_version": "1.0.0", "id": "test_item", "properties": {"datetime": "2024-05-10T15:53:16.721125Z"}, "geometry": {"type": "Point", "coordinates": [0, 0]}, "links": [], "assets": {}, "stac_extensions": []}'

def getItem(id:str):
    return item_json_str.replace("test_item",id)
def modItem(i:int):
    return item_json_str.replace("0, 0]",f"{i}, {i}]")




#result = runner.invoke(terrapi.stac_api_cli.stacApiCli, ["auth','--help'])
#click.echo(result.stdout)
#click.echo("   ")
#click.echo("   ")


#terrapi_cmd(["stac","login","--valid"])

if checkHelp:
    terrapi_cmd(["--help"])
    stac_cmd(['--help'], ["private","debug" ])
    stac_cmd(['auth','--help'], ["Usage","Options" ])
    stac_cmd(['login','--help'])
    for cmd in ["collection", "item"]:
        for sub in ["list", "get", "create", "update"]:
            stac_cmd([cmd,sub,'--help'])

if checkauth:
    stac_cmd(['auth','--help'], ["Usage","Options" ])
    stac_cmd(['login','--valid'],["Refresh Token valid till"])
    stac_cmd(["--debug",'auth',"-g"], ["GDAL_HTTP_BEARER"])
    stac_cmd(['auth',"-c"], ["Authorization: Bearer"])
    stac_cmd(['auth',"--wget"],["header"])
#stac_cmd(["auth", "--help"])
#cmd(["--debug", "login"])



if checkCollection:
    stac_cmd(["collection","list","-d", "-t", "--filter", "di39"])
    
    stac_cmd(["collection","list"])
    stac_cmd(["collection","get","di39rer.terrapi1","-p"])
  
    stac_cmd(["--debug","collection","delete","di39rer.terrapi1","--yes"], ["di39rer.terrapi1"])
    stac_cmd(["--debug","collection","get","di39rer.terrapi1"])

    stac_cmd(["collection","list"])
    stac_cmd(["collection","create","--id","di39rer.terrapi4","-u" ,"-j", collection_json_str])
    stac_cmd(["collection","list"], "di39rer.terrapi4")
    stac_cmd(["collection","delete","di39rer.terrapi4", "--yes"])
    stac_cmd(["collection","delete","di39rer.terrapi3", "--yes"])         
    stac_cmd(["collection","create","--id","di39rer.terrapi4","-u" ,"-j", collection_json_str])
    stac_cmd(["--debug","collection","update","--id","di39rer.terrapi4" ,"-j", collection_json_str.replace("Private User di39rer Test Collection","Updated Private Test Collection") ])
    stac_cmd(["collection","list", "-t"])


if checkItem:
    stac_cmd(["--debug","item","create","-j", item_json_str, "di39rer.terrapi4"])
    stac_cmd(["--debug","item","create","-j", getItem("superID"), "di39rer.terrapi4"])
    stac_cmd(["--debug","item","update","-j",modItem(3) , "di39rer.terrapi4"])

    stac_cmd(["item","list","di39rer.terrapi4"])
    stac_cmd(["item","delete","di39rer.terrapi4", "superID", "--yes"])
    stac_cmd(["item","list","di39rer.terrapi4"])

#stac_cmd(["--publicURL", "https://geoservice.dlr.de/eoc/ogc/stac", "collection", "list", "-t", "-d"])

#create when exists
if checkErrorCode:
    print("Item create test")
    stac_cmd(["item","create","-j", item_json_str, "di39rer.terrapi4"])
    print("Item test create existing item")
    stac_cmd(["item","create","-j", item_json_str, "di39rer.terrapi4"])
    print("Item test update existing item")
    stac_cmd(["item","update","-j", item_json_str, "di39rer.terrapi4"])

    stac_cmd(["item","delete", "di39rer.terrapi4","test_item","--yes"])
    print("Update non existing Item")
    stac_cmd(["item","update","-j", item_json_str, "di39rer.terrapi4"])


    stac_cmd(["collection","create","--id","di39rer.terrapi5","-u" ,"-j", collection_json_str])
    print("Create exiting collection")
    stac_cmd(["collection","create","--id","di39rer.terrapi5","-j", collection_json_str])
    stac_cmd(["--debug","collection","update","--id","di39rer.terrapi5" ,"-j", collection_json_str.replace("Private User di39rer Test Collection","Updated Private Test Collection") ])
    stac_cmd(["collection","delete","di39rer.terrapi5", "--yes"])  
    print("Update nonexiting collection")
    stac_cmd(["--debug","collection","update","--id","di39rer.terrapi5" ,"-j", collection_json_str.replace("Private User di39rer Test Collection","Updated Private Test Collection") ])

    print("Trying to create Collection of other user")
    stac_cmd(["--debug","collection","create","--id","di93bor.terror","-u" ,"-j", collection_json_str])

#stac_cmd(['auth'])
if checkPrefix:
    stac_cmd(['login',"--allowedPrefix"])

if checkPublic:
    stac_cmd(["--public","collection","list"])
    stac_cmd(["--public","collection","list", "--filter", "landsat.*", "-t", "-d"])
    stac_cmd(["--public","collection","get","cop-dem-glo-30", "--pretty"])
  
    

