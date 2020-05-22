import boto3
import uuid
import json
import os

from dto.message_dto import MessageDTO
from utils.log_util import LogUtil
from structlog import get_logger

log = LogUtil()

class SQSHelper:

    def send_message_batch(self, datas, client):
        
        queue_url = os.environ['FIFO_QUEUE_URL']
        
        batchSize = 10
        batchCount = 0
        batchEquals = 0

        send_message_batch_request_entries = []

        for data in datas:
            
            table_name = self.get_table_name(data['eventSourceARN'])

            try:
                
                message = MessageDTO(data, table_name).__dict__

                send_message_batch_request_entries.append(data)
                log.info(message)

                batchCount+=1

                if batchCount % batchSize == batchEquals:
                    client.send_message_batch(QueueUrl=queue_url, Entries=send_message_batch_request_entries)
                    send_message_batch_request_entries = []

            except Exception as e:
                log.error('ERROR processing message: {} due [{}]'.format(message, e))
                pass

        try:

            if send_message_batch_request_entries: 
                client.send_message_batch(QueueUrl=queue_url, Entries=send_message_batch_request_entries)
        
        except Exception as e:
            log.error('ERROR processing message: {} due [{}]'.format(message, e))
            pass


    def get_table_name(self, event_source_arn):
        return event_source_arn.split('/')[1]
