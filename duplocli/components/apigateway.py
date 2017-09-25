import click
import json
import datetime
import os
from common import CheckEmptyParam
from common import CheckAndGetConnection
from common import createApiGatewayApi
from common import getNameWithPrefix
from common import printSuccess
from common import getCloudResources

@click.group()
@click.pass_context
def apigateway(ctx):
    pass

@apigateway.command('create-api')
@click.option('--name', '-n', default='', help='Name of the lambda function')
@click.option('--lambdaa', '-l', default='', help='Name of the lambda function to link this to')
@click.pass_obj
def apigateway_add(ctx, name, lambdaa):
    tenant, token, url, tenantId = CheckAndGetConnection()
    CheckEmptyParam('name', name, "")
    if lambdaa is None:
        lambdaa = ""

    click.echo("Apigateway - Create API {} Lambda function {}".format(name, lambdaa))
    name =  getNameWithPrefix(name, tenant)
    jsondata = { "Name" : name, "LambdaFunction": lambdaa }
    createApiGatewayApi(token, url, tenantId, jsondata)
    printSuccess('Created ApiGateway {} .. It will available in about a min'.format(name))

@apigateway.command('delete-api')
@click.option('--name', '-n', default='', help='Name of the lambda function')
@click.pass_obj
def apigateway_add(ctx, name):
    tenant, token, url, tenantId = CheckAndGetConnection()
    CheckEmptyParam('name', name, "")

    click.echo("Apigateway - Delete API {}".format(name))
    name =  getNameWithPrefix(name, tenant)
    jsondata = { "Name" : name, "State": "delete" }
    createApiGatewayApi(token, url, tenantId, jsondata)
    printSuccess('Marked ApiGateway {} for delete .. It will removed in about a min'.format(name))

@apigateway.command('list-apis')
@click.pass_obj
def apigateway_list_functions(ctx):
    tenant, token, url, tenantId = CheckAndGetConnection()
    data = getCloudResources(tenant, token, url, tenantId)
    found = False
    for index, item in enumerate(data):
            if item["ResourceType"] == 8 :
                print("Api Gateway Rest API {}".format(item["Name"]))
                found = "true"        
    
    if not found:
        print("There no api gateway resourcs in the tenant. create one with create-api command")