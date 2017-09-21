import os
import json
import click
import requests
from os.path import expanduser
home = expanduser("~")

CONFIG_FILE = home + "/duplocli.config"
DUPLO_PREFIX = "duploservices-"

def getNameWithPrefix(name, tenant):
    if not name.startswith(DUPLO_PREFIX + tenant) :
        name = DUPLO_PREFIX + tenant + "-" + name 
    return name
        
def CheckEmptyParam(key, value, errmsg):
    if not value:
        raise click.BadParameter('{} cannot be empty. {}'.format(key, errmsg))

def GetConnection():
    with open(CONFIG_FILE) as json_file:
        json_data = json.load(json_file)
        tenant = json_data["DUPLO_TENANT_NAME"];
        token = json_data["DUPLO_TOKEN"];
        url = json_data["DUPLO_URL"];
        return tenant, token, url
    
    return None, None, None
        
# Check if the tenant name and API key is set
def CheckAndGetConnection():
    tenant, token, url = GetConnection()

    if tenant is None:
        raise click.BadParameter("Tenant Name is not set, call 'duplocli connect' to set session credentials")

    if url is None:
        raise click.BadParameter("URL is not set, call 'duplocli connect' to set session credentials")  
    
    if token is None:
        raise click.BadParameter("Token is not set, call 'duplocli connect' to set session credentials")
        
    # Login to Duplo and get tenants
    tenantId = validateTenantAccess(tenant, token, url) 
    return tenant, token, url, tenantId

def validateTenantAccess(tenant, token, url):
    url = url + "/admin/GetTenantsForUser"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal }
    r = requests.get(url, headers=headers)
    processStatusCode(r)

    json_data = json.loads(r.text)
    tenants = []
    print tenant
    for index, item in enumerate(json_data):
        if item["AccountName"] == tenant:
            return item["TenantId"]
        tenants.append(item["AccountName"])
        
    raise ValueError('You do not have access to tenant {} You only have access to tenants : {}'.format(tenant, ','.join(tenants)))

def checkAndCreateS3Bucket(name, tenant, token, url, tenantId):
    
    name = getNameWithPrefix(name, tenant)

    resourcesUrl = url + "/subscriptions/" + tenantId + "/GetCloudResources"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal }
    r = requests.get(resourcesUrl, headers=headers) 
    processStatusCode(r)
    
    json_data = json.loads(r.text)
    for index, item in enumerate(json_data):
        if item["ResourceType"] == 1 :
            if item["Name"].startswith(name) :
                print("Found the s3 bucket {}".format(item["Name"]))
                return item["Name"]

    # create the bucket as it is missing
    print('Creating S3 bucket {}'.format(name))
    s3bucketurl = url + "/subscriptions/" + tenantId + "/S3BucketUpdate"
    data = {'Name': name, "Type":"1"}
    lJsonData = json.dumps(data)
    r = requests.post(s3bucketurl, data=lJsonData, headers=headers)
    processStatusCode(r)

    print('Created S3 Bucket')
    return name

def createNewLambdaFunction(token, url, tenantId, funcObject):
    data = json.dumps(funcObject)
    newFuncUrl = url + "/subscriptions/" + tenantId + "/CreateLambdaFunction"
    
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal }
    r = requests.post(newFuncUrl, data=data, headers=headers)
    processStatusCode(r)

    print('Created Lambda Function {}'.format(funcObject["FunctionName"]))

def processStatusCode(r):
    if r.status_code == 401: 
        raise ValueError('Unauthorized. Login again using duplocli connection connect command ')
    print r.text    
    r.raise_for_status()
