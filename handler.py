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

if __name__ == "__main__":
    message = {'Records': [{'eventID': 'd0b2051b4b899ef0bca0731c3b96a73c', 'eventName': 'INSERT', 'eventVersion': '1.1', 'eventSource': 'aws:dynamodb', 'awsRegion': 'us-east-1', 'dynamodb': {'ApproximateCreationDateTime': 1590110663.0, 'Keys': {'uuid': {'S': '2'}}, 'NewImage': {'name': {'S': 'teste'}, 'uuid': {'S': '2'}}, 'SequenceNumber': '75941300000000022593736382', 'SizeBytes': 19, 'StreamViewType': 'NEW_AND_OLD_IMAGES'}, 'eventSourceARN': 'arn:aws:dynamodb:us-east-1:614858318717:table/replica-data/stream/2020-05-22T00:15:36.250'}]}
    handler(message, None)