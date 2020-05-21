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

    try:
        log.info('Sending Message To Queue with: {}'.format(len(datas)))
        sqs_helper.send_message_batch(datas)
    except Exception as exception:
        raise exception