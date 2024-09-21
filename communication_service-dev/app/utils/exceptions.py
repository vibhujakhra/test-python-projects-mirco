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


class KafkaProducerException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class KafkaConsumerException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class SendEmailException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message
