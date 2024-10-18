

from pydantic import BaseModel,EmailStr
from typing import List

class Registration(BaseModel):
    email_id:EmailStr
    password:str
    full_name:str
    max_trad_per_day:int =5
    base_stoploss:float =5.0
    base_target:float =10.0
    trailing_status:bool =True
    trailing_stoploss:float =10.0
    trailing_target:float =10.0
    description:str

class Login(BaseModel):
    user_id:str
    password:str


class Message(BaseModel):
    email : EmailStr
    subject : str
    message : str