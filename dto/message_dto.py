import uuid
import json 

class MessageDTO:

    def __init__(self, message_body, message_group_id):
        self.Id = str(uuid.uuid4())
        self.MessageBody = str(message_body.__dict__)
        self.MessageGroupId = message_group_id