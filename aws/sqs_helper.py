import boto3
import uuid
import json
import os

from structlog import get_logger

client = boto3.client('sqs')
LOG = get_logger()

class SQSHelper:

    def send_message(self, data, message_group_id):
        queue_url = os.environ['FIFO_QUEUE_NAME']
        message = str(data)
        
        try:
            client.send_message(QueueUrl=queue_url, MessageBody=message, MessageGroupId=message_group_id)
            LOG.info(event='REPLICA_DATA', message='Message Sent To The Queue: {}'.format(data))
        except Exception as exception:
            LOG.error(event='REPLICA_DATA', message='Error To Send Message {} To Queue With Exception: {}'.format(data, exception))
            raise exception

