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


class ConsentNotFoundException(Exception):
    def __init__(self):
        pass


class ConsentNotUpdatedException(Exception):
    def __init__(self):
        pass


class KafkaProducerException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class ChequeDetailsException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class PayInDataNotFoundException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class PayInSlipAlreadyGeneratedException(Exception):
    def __init__(self, message: str):
        self.message = message


class ColumnMisMatchError(Exception):
    def __init__(self, message: str):
        self.message = message


class DataverseNotRespondingError(Exception):
    def __init__(self, message: str):
        self.message = message


class ChequeNotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message


class PDFGenerationException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class EndorsementDataNotFoundException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class InvalidInputException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class EndorsementNumberNotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message


class PaymentNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        
        
        
class DealerCodeNotFound(Exception):
    def __init__(self, message):
        self.message = message


class FinalizedPaymentStatus(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message


class BillingStatusNotMappedException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

class InternalServerException(Exception):
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message