import boto3
import uuid
import json
import os

client = boto3.client('sqs')

class SQSHelper:

    def send_message(self, data):
        queue_url = os.environ['FIFO_QUEUE_NAME']
        message = str(data)
        print(type(message))
        client.send_message(QueueUrl=queue_url, MessageBody=message, MessageGroupId="123456")