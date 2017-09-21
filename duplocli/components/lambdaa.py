import click
import json
import datetime
from common import CheckEmptyParam
from common import CheckAndGetConnection
from common import checkAndCreateS3Bucket
from common import getNameWithPrefix
from awsutils import uploadFileToS3
from common import createNewLambdaFunction

import shutil

@click.group()
@click.pass_context
def lambdaa(ctx):
    pass

@lambdaa.command('deploy')
@click.option('--name', '-n', default='', help='Name of the lambda function')
@click.option('--config', '-c', default='', help='path to the json config file with lambda function specification')
@click.option('--dir', '-d', default='', help='code directory. The file with lambda entry point should be present at the root of this directory')
@click.pass_obj
def lambda_add(ctx, name, config, dir):
    tenant, token, url, tenantId = CheckAndGetConnection()
    CheckEmptyParam('name', name, "")
    CheckEmptyParam('config', config, "specify a valid path to config file")
    
    click.echo("Lambda Deploy - Function {} Config {}".format(name, config))
    funcObject = None
    name =  getNameWithPrefix(name, tenant)

    # Load the json file
    with open(config) as json_file:
    	json_data = json.load(json_file)
    	click.echo(json_data)
    	for index, item in enumerate(json_data["LambdaFunctions"]):
    		if getNameWithPrefix(item["FunctionName"], tenant) == name :
    			funcObject = item
    			break
    if funcObject is None:
    	raise ValueError('Failed to find desired function {} in config file'.format(name))			

    funcObject["FunctionName"] = getNameWithPrefix(funcObject["FunctionName"], tenant)
    fileVersion = funcObject["FunctionName"] + "-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    zipFilePath = "/tmp/" + fileVersion
    # zip the directory
    shutil.make_archive(zipFilePath, 'zip', dir)
    zipFilePath = zipFilePath + ".zip"
    localFileName = fileVersion + ".zip"

    # check if s3 bucket exists, if not create it
    bucketName = getNameWithPrefix("lambda-packages", tenant)
    bucketName = checkAndCreateS3Bucket(bucketName, tenant, token, url, tenantId)

    # Upload the file
    uploadFileToS3(token, tenantId, url, bucketName, zipFilePath, localFileName)

    # Create Function
    funcObject["Code"] = {"S3Bucket" : bucketName, "S3Key":localFileName };
    print("Creating lambda function {}".format(funcObject["FunctionName"]))
    createNewLambdaFunction(token, url, tenantId, funcObject)

