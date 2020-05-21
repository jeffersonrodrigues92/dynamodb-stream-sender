import json 

from dto.log_data_dto import LogDataDTO
from structlog import get_logger


log = get_logger()

class LogUtil:

    @staticmethod
    def info(message):
        log.info(json.dumps(LogDataDTO(message).__dict__))

    @staticmethod
    def warn(message):
        log.warn(json.dumps(LogDataDTO(message).__dict__))

    @staticmethod
    def error(message):
        log.error(json.dumps(LogDataDTO(message).__dict__))
