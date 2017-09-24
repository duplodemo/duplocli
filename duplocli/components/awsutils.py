import os
import json
import click
import requests
import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from common import processStatusCode

def getAwsToken(token, tenantId, url):
    resourcesUrl = url + "/subscriptions/" + tenantId + "/GetAwsConsoleTokenUrl"
    headerVal = "Bearer " + token
    headers = { 'Authorization' : headerVal }
    r = requests.get(resourcesUrl, headers=headers) 
    processStatusCode(r)
    json_data = json.loads(r.text)
    key = json_data["AccessKeyId"]
    value = json_data["SecretAccessKey"]
    ststoken = json_data["SessionToken"]

    return key, value, ststoken

def uploadFileToS3(token, tenantId, url, bucketName, localfile, remotefilename):
    print("Uploading file {} to S3 Bucket {}".format(localfile, bucketName))
    key, value, ststoken = getAwsToken(token, tenantId, url)
    conn = boto.s3.connect_to_region('us-west-2', aws_access_key_id=key, aws_secret_access_key=value, security_token=ststoken)
    # upload the file
    b = conn.get_bucket(bucketName)
    k = Key(b)
    k.key = remotefilename
    k.set_contents_from_filename(localfile)
    print("Uploading file {} to S3 Bucket {}".format(remotefilename, bucketName))

