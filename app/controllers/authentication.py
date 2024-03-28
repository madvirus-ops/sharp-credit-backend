import sys

sys.path.append("./")

import json
import random
import uuid
from datetime import datetime, timedelta

import pytz
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from connections.models import SalaryRequests, Borrower, VerificationCodes, tz
from helpers.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from helpers.users import UserHelper
from helpers.validations import validate_email, validate_phone_number
from remita.helpers import getCustomerByPhonenumber, getCustomerByAccount
from response import responses as r


def create_user_account(
    phone_number: str,
    account_number: str,
    bank_code: str,
    password: str,
    db: Session,
):
    try:

        

        borrower_id = uuid.uuid4().hex

        if phone_number.startswith("234"):
            phone_number = "0" + phone_number[3:]

        user = db.query(Borrower).filter(Borrower.phone_number == phone_number).first()

        if user:
            return r.user_exist_phone

        request = getCustomerByAccount(bank_code,account_number,db)
        if request["code"] != 200:
            return r.error_occured

        first_name = request["first_name"]
        last_name = request["last_name"]
        bvn = request["bvn"]
        response_id = request["response_id"]

        update_request = (
            db.query(SalaryRequests)
            .filter(SalaryRequests.response_id == response_id)
            .first()
        )

        help = UserHelper(db, borrower_id).createUser(
            first_name, last_name, phone_number, "", password
        )
        if help["code"] == 200:
            user = (
                db.query(Borrower).filter(Borrower.borrower_id == borrower_id).first()
            )
            user.bvn = bvn
            user.phone_number_verified = True
            update_request.borrower_id = borrower_id
            db.commit()

            # resend_signup_email_verification(email, db)
            # resend_signup_phone_vefification(phone_number, db)

            return {
                "success": True,
                "code": 201,
                "message": "You have successfully created your account",
                "data": {"borrower_id": help["borrower_id"]},
            }
        return help

    except Exception as e:
        print(e.args)
        return r.error_occured


def resend_signup_email_verification(email: str, db: Session):
    try:
        user = db.query(Borrower).filter(Borrower.email == email).first()
        if user is None:
            return r.user_notfound
        code = random.randint(20000, 99999)
        add1 = VerificationCodes(
            borrower_id=user.borrower_id,
            code=code,
            expires=datetime.now(tz) + timedelta(minutes=10),
        )
        db.add(add1)
        db.commit()
        print(code)
        # sendVerificationEmail(email, user.first_name, code)
        return r.otp_sent
    except Exception as e:
        print(e.args)
        return r.error_occured


def resend_signup_phone_vefification(phonenumber: str, db: Session):
    try:
        user = (
            db.query(Borrower)
            .filter(
                or_(
                    Borrower.phone_number == phonenumber.lower().strip(),
                    Borrower.email == phonenumber.lower().strip(),
                )
            )
            .first()
        )
        if not user:
            return r.user_notfound

        code = random.randint(20000, 99999)
        add1 = VerificationCodes(
            borrower_id=user.borrower_id,
            code=code,
            expires=datetime.now() + timedelta(minutes=10),
        )
        db.add(add1)
        print(code)
        db.commit()
        message = f"Hi, You requested to create an account, your One time password is {code}. Expires in 10 minutes"

        # send_sms_notification(phonenumber, message, db)

        return r.otp_sent

    except Exception as e:
        print(e.args)
        return r.error_occured


def verify_signup_email(email: str, code: str, db: Session):
    try:
        user = db.query(Borrower).filter(Borrower.email == email).first()

        if user is None:
            return r.user_notfound

        ver_code = (
            db.query(VerificationCodes)
            .filter(
                VerificationCodes.borrower_id == user.borrower_id,
                VerificationCodes.code == code,
            )
            .first()
        )

        if ver_code is None:
            return r.invalid_code

        if datetime.now().replace(tzinfo=pytz.UTC) > ver_code.expires.replace(
            tzinfo=pytz.UTC
        ):
            return r.code_expired

        else:
            user.email_verified = True
            user.updated_at = datetime.now(tz)
            db.delete(ver_code)
            db.commit()
            return {
                "success": True,
                "code": 200,
                "message": "Email verified successfully",
                "data": {
                    "borrower_id": user.borrower_id,
                    "full_name": f"{user.first_name} {user.last_name}",
                },
            }
    except Exception as e:
        print(e.args)
        return r.error_occured


def verify_signup_phone_number(phone_number: str, code: str, db: Session):
    try:
        phonenumber = phone_number

        user = db.query(Borrower).filter(Borrower.phone_number == phonenumber).first()

        if user is None:
            return r.user_notfound

        ver_code = (
            db.query(VerificationCodes)
            .filter(
                VerificationCodes.borrower_id == user.borrower_id,
                VerificationCodes.code == code,
            )
            .first()
        )

        if ver_code is None:
            return r.invalid_code

        print(
            datetime.now(tz).replace(tzinfo=pytz.UTC),
            ver_code.expires.replace(tzinfo=pytz.UTC),
        )

        if datetime.now().replace(tzinfo=pytz.UTC) > ver_code.expires.replace(
            tzinfo=pytz.UTC
        ):
            return r.code_expired

        else:
            user.phone_number_verified = True
            user.updated_at = datetime.now(tz)
            db.delete(ver_code)
            db.commit()
            return {
                "success": True,
                "code": 200,
                "message": "phone number verified",
                "data": {"phonenumber": phonenumber},
            }
    except Exception as e:
        print(e.args)
        return r.error_occured


def login_with_password(
    phone_number: str,
    password: str,
    db: Session,
):
    try:

        login = UserHelper(db).login_user(phone_number.lower(), password)
        if login["code"] == 404:
            return r.user_notfound
        elif login["code"] == 400:
            return r.invalid_login
        # elif login["code"] == 413:
        #     return r.email_notverified
        elif login["code"] == 414:
            return r.phone_notverified

        else:
            user = login["user"]
            access_token = create_access_token(
                {"id": user.borrower_id, "email": user.email}
            )
            refresh_token = create_refresh_token(
                {"id": user.borrower_id, "email": user.email}
            )
            if refresh_token["code"] == 200 and access_token["code"] == 200:
                return {
                    "message": "Logged in successfully",
                    "code": 200,
                    "success": True,
                    "data": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                }
            return r.error_occured
    except Exception as e:
        print(e.args)
        return r.error_occured


def send_pin_reset_code(email: str, db: Session):
    try:
        user = (
            db.query(Borrower).filter(Borrower.email == email.lower().strip()).first()
        )
        if user is None:
            return r.user_notfound
        code = random.randint(20000, 99999)
        add1 = VerificationCodes(
            borrower_id=user.borrower_id,
            code=code,
            expires=datetime.now() + timedelta(minutes=10),
        )
        db.add(add1)
        db.commit()
        print(code)

        message = f"Hi {str(user.first_name).capitalize()}, You requested a reset, your One time password is {code}. Expires in 10 minutes"

        # send_sms_notification(phonenumber, message, db)

        return r.otp_sent
    except Exception as e:
        print(e.args)
        return r.error_occured


def verify_password_reset(email: str, new_password: str, code: str, db: Session):
    try:
        user = (
            db.query(Borrower).filter(Borrower.email == email.lower().strip()).first()
        )

        if user is None:
            return r.user_notfound

        ver_code = (
            db.query(VerificationCodes)
            .filter(
                VerificationCodes.borrower_id == user.borrower_id,
                VerificationCodes.code == code,
            )
            .first()
        )

        if ver_code is None:
            return r.invalid_code

        if datetime.now().replace(tzinfo=pytz.UTC) > ver_code.expires.replace(
            tzinfo=pytz.UTC
        ):
            return r.code_expired

        else:
            if UserHelper(db, user.borrower_id).setUserPassword(new_password):
                user.updated_at = datetime.now(tz)
                db.delete(ver_code)
                db.commit()

                return {
                    "code": 200,
                    "message": "Password reset successfully",
                    "success": True,
                    "data": {"borrower_id": user.borrower_id},
                }

            return r.password_notset
    except Exception as e:
        print(e.args)
        return r.error_occured


def verify_refresh_access_token(
    token: str,
    db: Session,
):
    try:
        result = verify_refresh_token(token)

        if result["code"] != 200:
            return {
                "code": 401,
                "status": "error",
                "message": "Invalid authorization token or token Expired.",
            }

        user = db.query(Borrower).filter(Borrower.borrower_id == result["id"]).first()

        if user.account_deleted:
            return {
                "code": 401,
                "status": "error",
                "message": "User Not Found",
            }

        if user.is_restricted:
            return {
                "code": 401,
                "status": "error",
                "message": "Your account is suspended, please contact support",
            }

        access_token = create_access_token(
            {"id": user.borrower_id, "email": user.email}
        )
        refresh_token = create_refresh_token(
            {"id": user.borrower_id, "email": user.email}
        )
        if refresh_token["code"] == 200 and access_token["code"] == 200:
            return {
                "message": "token refreshed successfully",
                "code": 200,
                "success": True,
                "data": {
                    "access": access_token,
                    "refresh": refresh_token,
                },
            }
        return r.error_occured
    except Exception as e:
        print(e.args)
