import datetime
from fastapi import status, HTTPException


def check_token_expiry(reset_token_dict):
    expiry_time = reset_token_dict["exp_time"]
    # whether the token is expired or not
    if expiry_time < datetime.datetime.now().timestamp():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TOKEN_EXPIRED",
            headers={"WWW-Authenticate": "Bearer"},
        )
