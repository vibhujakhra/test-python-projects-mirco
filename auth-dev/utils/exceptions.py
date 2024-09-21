class DatabaseConnectionException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class UpdateRecordException(DatabaseConnectionException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class InsertRecordException(DatabaseConnectionException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class KafkaProducerException(DatabaseConnectionException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class InvalidRoleException(DatabaseConnectionException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class InvalidModuleCodeException(DatabaseConnectionException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class GetAPIException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message