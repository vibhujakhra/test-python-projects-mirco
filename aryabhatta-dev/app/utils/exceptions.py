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
