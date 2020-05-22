import boto3
import os

from datetime import datetime, timedelta
from utils.log_util import LogUtil
from aws.sqs_helper import SQSHelper

now = datetime.now()
log = LogUtil()
sqs_helper = SQSHelper()

def handler(event, context):

    datas = event['Records']
    replica_region = os.environ['REPLICA_REGION']
    account_region = os.environ['ACCOUNT_REPLICA']

    try:
        log.info('Sending Message To Queue with: {}'.format(len(datas)))
        client = assume_role(account_region, 'SenderStreamSQSRole', 'sqs', replica_region)
        sqs_helper.send_message_batch(datas, client)
    except Exception as exception:
        raise exception

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
        log.error('Error To Assume Role With Exception{}'.format(exception))
        raise exception
    
    log.info('Role Assumed with Succeed')
    
    return client_resource