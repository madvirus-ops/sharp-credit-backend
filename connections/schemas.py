from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


class Signup(BaseModel):
    email: str
    password: str
    phone_number: str


class LoginEmail(BaseModel):
    username: str
    password: str


class EmailVerify(BaseModel):
    email: str
    code: str


class PhoneVerify(BaseModel):
    phonenumber: str
    code: str


class USerEmail(BaseModel):
    email: EmailStr


class ResetPassword(USerEmail):
    new_password: str
    code: str


class Setusername(BaseModel):
    user_id: str
    username: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class TokenBody(BaseModel):
    token:str