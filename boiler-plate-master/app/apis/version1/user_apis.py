import logging
from typing import List

from fastapi import APIRouter, Depends

from app.models.users import Users
from app.schemas.users import *
from app.utils.code_utils import generate_user_code

router = APIRouter()
logger = logging.getLogger("api")


@router.get("/fetch_all_user/")
async def fetch_all_user() -> List[UserResponse]:
    """
    The fetch_all_user function returns a list of all users in the database.
        Returns:
            List[UserResponse]: A list of UserResponse objects, each representing a user in the database.
    :return: A list of UserResponse objects
    """
    user_objects = await Users.fetch_all()
    return [UserResponse(**user_object.__dict__) for user_object in user_objects]


@router.get("/fetch_all_active_user/")
async def fetch_all_active_user() -> List[UserResponse]:
    """
    The fetch_all_active_user function returns a list of all active users in the database.

    :return: A list of UserResponse objects
    
    """
    user_objects = await Users.fetch_all(is_active=True)
    return [UserResponse(**user_object.__dict__) for user_object in user_objects]


@router.get("/get_user_by_id/")
async def get_user_by_id(user_id: int) -> UserResponse:
    """
    The get_user_by_id function returns a UserResponse object containing the user's information.

    :param user_id:int: Specify the type of the parameter, and also to give it a name
    :return: A UserResponse object
    
    """
    user_object = await Users.fetch(key=user_id)
    return UserResponse(**user_object.__dict__)


@router.get("/get_user_by_code/")
async def get_user_by_id(user_code: str) -> UserResponse:
    """
    The get_user_by_id function is a ReST endpoint that returns the user object
        associated with the given user_code.

    :param user_code:str: Specify the type of data that is being passed in
    :return: A UserResponse object
    
    """
    user_object = await Users.fetch_by_code(code=user_code)
    return UserResponse(**user_object.__dict__)


@router.post("/add_user/")
async def add_user(new_user_data: CreateUserRequest) -> UserResponse:
    """
    The add_user function creates a new user in the database.

    :param new_user_data:CreateUserRequest: Specify the type of data that is expected to be passed into the function
    :return: A UserResponse object
    """
    user_data = new_user_data.__dict__
    user_data["code"] = generate_user_code()
    user_object = await Users.create(**user_data)
    from pprint import pprint
    pprint(user_object.__dict__)
    return UserResponse(**user_object.__dict__)


@router.patch("/update_user/{user_id}")
async def update_user(user_id: int, user_data: UpdateUserRequest = Depends()) -> UserResponse:
    """
    The add_user function is used to add a new user to the database.
        The function takes in a user_id and an optional UpdateUserRequest object, which contains all of the information
        that can be updated about a user. If no UpdateUserRequest object is passed into the function, then it will
        default to an empty one. The function then updates the database with this information using Users' update
        method and returns a UserResponse object containing all of this data.

    :param user_id:int: Specify the user id of the user to be updated
    :param user_data:UpdateUserRequest=Depends(): Pass the user data to the function
    :return: A UserResponse object, which is a dict-like object
    """
    user_data = user_data.__dict__
    user_data = {k: v for k, v in user_data.items() if v}
    from pprint import pprint
    pprint(user_data)
    await Users.update(key=user_id, **user_data)
    user_object = await Users.fetch(key=user_id)

    return UserResponse(**user_object.__dict__)
