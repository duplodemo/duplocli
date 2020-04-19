import click
import json
import datetime
import os
from common import CheckEmptyParam
from common import CheckAndGetConnection
from common import checkAndCreateS3Bucket
from common import getNameWithPrefix
from awsutils import uploadFileToS3
from common import createLambdaFunction
from common import deleteLambdaFunction
from common import updateLambdaFunctionConfig
from common import updateLambdaFunctionCode
from common import listLambdaFunctions
from common import printSuccess
import common

import shutil

@click.group()
@click.pass_context
def hosts(ctx):
    pass

@hosts.command('list-hosts')
@click.pass_obj
def hosts_list_aws(ctx):
    tenant, token, url, tenantId = CheckAndGetConnection()
    common.getHosts(tenant, token, url, tenantId)

@hosts.command('list-minions')
@click.pass_obj
def hosts_list_minions(ctx):
    tenant, token, url, tenantId = CheckAndGetConnection()
    common.getMinions(tenant, token, url, tenantId)
