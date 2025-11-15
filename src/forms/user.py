from pydantic import BaseModel 


class UserLoginForm(BaseModel):
    username: str 
    password: str 


class UserRegistrationForm(BaseModel):
    username: str 
    password: str 


class UserForm(BaseModel):
    username: str 
    uuid: str 


class UsersListForm(BaseModel):
    users: list[UserForm]

