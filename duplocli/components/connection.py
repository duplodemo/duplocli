import click
import json
import os
from common import CheckEmptyParam
from common import CONFIG_FILE

@click.group()
@click.pass_context
def connection(ctx):
    pass

@connection.command('connect')
@click.option('--tenant', '-t', default='', help='Name of the tenant or workspace. You can find this at the top right in the DuploCloud UI')
@click.option('--url', '-c', default='', help='url of the duplocloud service you are subscribed to. For example https://portal.duplocloud.net')
@click.option('--key', '-k', default='', help='Api key to connect to duplocloud service you are subscribed to')
@click.pass_obj
def set_connection(ctx, tenant, url, key):
    
    CheckEmptyParam('tenant', tenant, "tenant name cannot be empty")
    CheckEmptyParam('url', url, "url cannot be empty")
    CheckEmptyParam('key', key, "token cannot be empty")

    data = json.dumps({'DUPLO_TENANT_NAME': tenant, 'DUPLO_TOKEN': key, 'DUPLO_URL': url})
    file = open(CONFIG_FILE, "w")
    file.write(data)
    file.close()