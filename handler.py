import boto3
import os

from datetime import datetime, timedelta
from structlog import get_logger
from aws.sqs_helper import SQSHelper

now = datetime.now()
LOG = get_logger()
sqs_helper = SQSHelper()

def handler(event, context):

    region = os.environ['REGION_REPLICA']
    account_dr = os.environ['ACCOUNT_REPLICA']
    datas = event['Records']

    client = assume_role(account_dr, "ReplicaDataManagerRole", "dynamodb", region)

    for data in datas:
        LOG.info(event='REPLICA_DATA', message='Replica Data: {}'.format(data))
        replica_data(client, data)

def replica_data(client, data):
   
   event_name = data['eventName']
   table_name = get_table_name(data['eventSourceARN'])

   LOG.info(event='REPLICA_DATA', message='Event Name: {} and Data: {}'.format(event_name, data))

   try:
    
        if event_name == 'INSERT' or event_name == 'MODIFY':
            client.put_item(TableName=table_name, Item=data['dynamodb']['NewImage'])
            LOG.info(event='REPLICA_DATA', message='Table {} in DR Will Be Receive {} in with Data {} '.format(table_name, event_name, data))
        else:
            client.delete_item(TableName=table_name, Item=data['dynamodb']['Keys'])
            LOG.info(event='REPLICA_DATA', message='Table {} in DR  Will Be Receive {} in with Data {} '.format(table_name, event_name, data))
        
   except Exception as exception:
        LOG.error(event='REPLICA_DATA', message='Error To {} in Table {} To The Item {} With Exception {}'.format(event_name, table_name, data, exception))
        sqs_helper.send_message(data)
        raise exception


def get_table_name(event_source_arn):
    return event_source_arn.split('/')[1]


def assume_role(account, role, resource, region):

    try:
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
    except Exception as exception:
        LOG.error(event='REPLICA_DATA', message='Error To Assume Role With Exception{}'.format(exception))
        sqs_helper.send_message(data)
        raise exception
    
    LOG.info(event='REPLICA_DATA', message='Item Assumed with Succeed')
    return client_resource