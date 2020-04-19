import os
import sys
import datetime
import json
import click
import requests
from common import CheckEmptyParam
from common import CheckAndGetConnection
from common import getNameWithPrefix
from common import printSuccess
from common import processStatusCode
import common
from common import printSuccess
import shutil

@click.group()
@click.pass_context
def blueprints(ctx):
    pass

@blueprints.command('export-tenant')
@click.pass_obj
def blueprints_export_tenant(ctx):
    tenant, token, url, tenantId = CheckAndGetConnection()
    jsondata = { "IncludeAwsHosts" : "true" }
    export_tenant(token,url, tenantId, jsondata)

def export_tenant(token, url, tenantId, funcObject):
    newFuncUrl = url + "/subscriptions/" + tenantId + "/ExportTenant"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal, 'content-type': 'application/json' }
    data = json.dumps(funcObject)
    r = requests.post(newFuncUrl, data=data, headers=headers)
    processStatusCode(r)
    data = json.loads(r.text)
    data = common.remove_empty_elements(data)
    formattedData = json.dumps(data, indent=4, sort_keys=True)
    print(formattedData)
