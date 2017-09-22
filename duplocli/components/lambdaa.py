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

import shutil

@click.group()
@click.pass_context
def lambdaa(ctx):
    pass

@lambdaa.command('create-function')
@click.option('--name', '-n', default='', help='Name of the lambda function')
@click.option('--config', '-c', default='', help='path to the json config file with lambda function specification')
@click.option('--package', '-p', default='', help='code directory or path to a zip file. The file with lambda entry point should be present'\
' at the root of this zip folder (upon unzipping) or directory. If you specify a directory then this command will create a zip file in temp directory and use that'\
' See for details on how to create deployment package zip files http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html')
@click.pass_obj
def lambda_add(ctx, name, config, package):
    lambda_add_or_update(ctx, name, config, package, False)

@lambdaa.command('update-function-code')
@click.option('--name', '-n', default='', help='Name of the lambda function')
@click.option('--config', '-c', default='', help='path to the json config file with lambda function specification')
@click.option('--package', '-p', default='', help='code directory or a zip file. The file with lambda entry point should be present'\
' at the root of this zip folder (upon unzipping) or directory. If you specify a directory then this command will create a zip file in temp directory and use that'\
' See for details on how to create deployment package zip files http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html')
@click.pass_obj
def lambda_function_update_code(ctx, name, config, package):
    lambda_add_or_update(ctx, name, config, package, True)

def lambda_add_or_update(ctx, name, config, dir, update):
    tenant, token, url, tenantId = CheckAndGetConnection()
    CheckEmptyParam('name', name, "")
    CheckEmptyParam('config', config, "specify a valid path to config file")
    
    click.echo("Lambda Deploy - Function {} Config {}".format(name, config))
    funcObject = None
    name =  getNameWithPrefix(name, tenant)

    # Load the json file
    with open(config) as json_file:
    	json_data = json.load(json_file)
    	for index, item in enumerate(json_data["LambdaFunctions"]):
    		if getNameWithPrefix(item["FunctionName"], tenant) == name :
    			funcObject = item
    			break
    if funcObject is None:
    	raise ValueError('Failed to find desired function {} in config file'.format(name))			

    funcObject["FunctionName"] = getNameWithPrefix(funcObject["FunctionName"], tenant)
    zipFilePath = ""
    if dir.endswith(".zip"):
        zipFilePath = dir
        localFileName = os.path.basename(dir)
    else:        
        fileVersion = funcObject["FunctionName"] + "-" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        zipFilePath = "/tmp/" + fileVersion
        print('Making a zip file {} from folder {}'.format(zipFilePath + ".zip", dir))
        # zip the directory
        shutil.make_archive(zipFilePath, 'zip', dir)
        zipFilePath = zipFilePath + ".zip"
        localFileName = fileVersion + ".zip"

    # check if s3 bucket exists, if not create it
    bucketName = getNameWithPrefix("lambda-packages", tenant)
    bucketName = checkAndCreateS3Bucket(bucketName, tenant, token, url, tenantId)

    # Upload the file
    uploadFileToS3(token, tenantId, url, bucketName, zipFilePath, localFileName)
    
    if not update:
        # Create Function
        funcObject["Code"] = {"S3Bucket" : bucketName, "S3Key":localFileName };
        print("Creating lambda function {}".format(funcObject["FunctionName"]))
        createLambdaFunction(token, url, tenantId, funcObject)
        printSuccess('Created Lambda Function {}'.format(funcObject["FunctionName"]))
    else:
        print("Updating lambda function code {}".format(funcObject["FunctionName"]))
        data = {"FunctionName" : funcObject["FunctionName"], "S3Bucket": bucketName, "S3Key":localFileName }
        updateLambdaFunctionCode(token, url, tenantId, data)
        printSuccess('Updated Lambda Function {} code'.format(funcObject["FunctionName"]))


@lambdaa.command('delete-function')
@click.option('--name', '-n', default='', help='Name of the lambda function')
@click.pass_obj
def lambda_delete(ctx, name):
    tenant, token, url, tenantId = CheckAndGetConnection()
    CheckEmptyParam('name', name, "")
    click.echo("Lambda - Delete Function {} ".format(name))
    name =  getNameWithPrefix(name, tenant)
    deleteLambdaFunction(token, url, tenantId, name)
    printSuccess('Deleted Lambda Function {}'.format(name))


@lambdaa.command('update-function-configuration')
@click.option('--name', '-n', default='', help='Name of the lambda function')
@click.option('--config', '-c', default='', help='path to the json config file with lambda function specification')
@click.pass_obj
def lambda_function_update_config(ctx, name, config):
    tenant, token, url, tenantId = CheckAndGetConnection()
    CheckEmptyParam('name', name, "")
    CheckEmptyParam('config', config, "specify a valid path to config file")
    
    click.echo("Lambda Update - Function {} Config {}".format(name, config))
    funcObject = None
    name =  getNameWithPrefix(name, tenant)

    # Load the json file
    with open(config) as json_file:
        json_data = json.load(json_file)
        for index, item in enumerate(json_data["LambdaFunctions"]):
            if getNameWithPrefix(item["FunctionName"], tenant) == name :
                funcObject = item
                break
    if funcObject is None:
        raise ValueError('Failed to find desired function {} in config file'.format(name))          
    
    funcObject["FunctionName"] = getNameWithPrefix(funcObject["FunctionName"], tenant)
    # Create Function
    print("Updating lambda function {}".format(funcObject["FunctionName"]))
    updateLambdaFunctionConfig(token, url, tenantId, funcObject)
    printSuccess('Updated Lambda Function {} configuration'.format(name))

@lambdaa.command('list-functions')
@click.pass_obj
def lambda_list_functions(ctx):
    tenant, token, url, tenantId = CheckAndGetConnection()
    listLambdaFunctions(tenant, token, url, tenantId)
