class DatabaseException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class DatabaseConnectionException(DatabaseException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class UpdateRecordException(DatabaseException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class InsertRecordException(DatabaseException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class RecordNotFoundException(DatabaseException):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

class DealerCodeAlreadyExistException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class WorkshopCodeAlreadyExistException(Exception):
    def __init__(self,name: str, message: str):
        self.name = name
        self.message = message

class UserAlreadyExistException(Exception):
    def __init__(self,name: str, message: str):
        self.name = name
        self.message = message
