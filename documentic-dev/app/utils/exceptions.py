class DatabaseConnectionException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class UpdateRecordException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class InsertRecordException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class KafkaPublishToQueueException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class PDFGenerationException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class GetAPIException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message
