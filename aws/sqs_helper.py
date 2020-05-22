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
        
        queue_url ='https://sqs.us-east-1.amazonaws.com/614858318717/queueReplicaStreamData.fifo'
        
        batchSize = 10
        batchCount = 0
        batchEquals = 0

        send_message_batch_request_entries = []

        for data in datas:
            

            try:
                
                table_name = self.get_table_name(data['eventSourceARN'])
                message = MessageDTO(data, table_name)

                send_message_batch_request_entries.append(message)
                log.info(message)

                batchCount+=1

                if batchCount % batchSize == batchEquals:
                    log.info("enviando mensagens {}".format(send_message_batch_request_entries))
                    client.send_message_batch(QueueUrl=queue_url, Entries=send_message_batch_request_entries)
                    send_message_batch_request_entries = []

            except Exception as e:
                log.error('ERROR processing message: {}'.format(e))
                pass

        try:

            if send_message_batch_request_entries: 
                client.send_message_batch(QueueUrl=queue_url, Entries=send_message_batch_request_entries)
        
        except Exception as e:
            log.error('ERROR processing message: {} due [{}]'.format(message, e))
            pass


    def get_table_name(self, event_source_arn):
        return event_source_arn.split('/')[1]
