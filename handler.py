import boto3
from datetime import datetime, timedelta
#from structlog import get_logger
import os

now = datetime.now()
#LOG = get_logger()


def handler(event, context):
    region = os.environ['REGION']
    account_dr = os.environ['ACCOUNT_DR']
    datas = event['Records']
    client = assume_role(account_dr, "ACLManageRole", "dynamodb", region)

    for data in datas:
        replica_data(client, data)

def replica_data(client, data):
   
   event_name = data['eventName']
   table_name = get_table_name(data['eventSourceARN'])

   if event_name == 'INSERT' or event_name == 'MODIFY':
       client.put_item(TableName=table_name, Item=data['dynamodb']['NewImage'])
   else:
       client.delete_item(TableName=table_name, Item=data['dynamodb']['Keys'])

def get_table_name(event_source_arn):
    return event_source_arn.split('/')[1]


def assume_role(account, role, resource, region):
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn="arn:aws:iam::" + account + ":role/" + role,
        RoleSessionName=role
    )
    credentials = assumed_role_object['Credentials']
    client_resource = boto3.client(
        resource,
        region_name=region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
    return client_resource