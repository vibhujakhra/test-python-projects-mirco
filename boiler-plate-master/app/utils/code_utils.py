from uuid import uuid4


def generate_user_code() -> str:
    """
    this method is used to generate unique string everytime for
    request id. current logic is to generate unique uuid as request id
    """
    return str(uuid4())
