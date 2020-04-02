import boto3
import uuid
import os

client = boto3.client('sqs')

class SQSHelper:

    def send_message(self, data):
        queue_url = os.environ['FIFO_QUEUE_NAME']
        client.send_message(QueueUrl=queue_url, MessageBody=data, MessageGroupId="123456")