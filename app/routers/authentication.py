import sys
sys.path.append("./")

from fastapi import APIRouter, BackgroundTasks, Depends, Response, Request, Header
import re
from connections.database import get_db
from connections.schemas import (
    LoginEmail,
    Signup,
    EmailVerify,
    PhoneVerify,
    EmailVerify,
    USerEmail,
    ResetPassword,

)
from app.controllers.authentication import *


router = APIRouter(prefix="/api/v2/auth", tags=["Authentication"])


@router.post("/signup")
async def Sign_up(
    body: Signup,
    task: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
):
    result = create_user_account(
        body.first_name,
        body.last_name,
        body.phone_number,
        body.email,
        body.password,
        db,
    )
    response.status_code = result["code"]
    return result


@router.get("/resend/email")
async def resend_email_verification(
    email: str, response: Response, db: Session = Depends(get_db)
):
    result = resend_signup_email_verification(email, db)
    response.status_code = result["code"]
    return result


@router.get("/resend/phone")
async def resend_sms_verification(
    phone_number: str, response: Response, db: Session = Depends(get_db)
):
    result = resend_signup_phone_vefification(phone_number, db)
    response.status_code = result["code"]
    return result


@router.post("/verify/email")
async def verify__email(
    body: EmailVerify,
    task: BackgroundTasks,
    response: Response,
    db: Session = Depends(get_db),
):
    result = verify_signup_email(body.email, body.code, db)
    response.status_code = result["code"]
    return result


@router.post("/verify/phone")
async def verify_phone__number(
    body: PhoneVerify,
    response: Response,
    db: Session = Depends(get_db),
):
    result = verify_signup_phone_number(body.phonenumber, body.code, db)
    response.status_code = result["code"]
    return result


@router.post("/login/password")
async def login_with__password(
    body: LoginEmail,
    response: Response,
    db: Session = Depends(get_db),
):
    result = login_with_password(
        body.email,
        body.password,
        db,
    )
    response.status_code = result["code"]

    return result


@router.post("/reset/send-otp")
async def send_reset_otp(
    body: USerEmail,
    response: Response,
    db: Session = Depends(get_db),
):

    result = send_pin_reset_code(body.phone_number, db)
    response.status_code = result["code"]
    return result



@router.post("/reset/password")
async def reset_user_password(
    body: ResetPassword,
    response: Response,
    db: Session = Depends(get_db),
):
    result = verify_password_reset(body.email, body.new_password, body.code, db)
    response.status_code = result["code"]
    return result
