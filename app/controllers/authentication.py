import sys

sys.path.append("./")

from helpers.users import UserHelper
from connections.models import Users, VerificationCodes, tz
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, asc, func
from response import responses as r
import pytz
from helpers.validations import validate_email, validate_phone_number
from helpers.security import create_access_token,create_refresh_token
import uuid


def create_user_account(
    first_name: str,
    last_name: str,
    phone_number: str,
    email: str,
    password: str,
    db: Session,
):
    try:
        if len(first_name) < 3 or len(last_name) < 3:
            return r.invalid_name

        val_phon = validate_phone_number(phone_number, db)
        val_email = validate_email(email, db)

        if val_phon["code"] == 400 or val_email["code"] == 400:
            return val_phon

        if val_phon["code"] == 201 or val_email["code"] == 201:
            ress = resend_signup_phone_vefification(phone_number, db)
            ress2 = resend_signup_email_verification(email, db)
            return ress

        user_id = uuid.uuid4().hex
        phone_number = val_phon["phone_number"]

        help = UserHelper(db, user_id).createUser(
            first_name, last_name, phone_number, email, password
        )
        if help["code"] == 200:
            resend_signup_email_verification(email, db)
            resend_signup_phone_vefification(phone_number, db)
            return {
                "success": True,
                "code": 201,
                "message": "You have successfully created your account",
                "data": {"user_id": help["user_id"]},
            }
        return help
    except Exception as e:
        print(e.args)
        return r.error_occured


def resend_signup_email_verification(email: str, db: Session):
    try:
        user = db.query(Users).filter(Users.email == email).first()
        if user is None:
            return r.user_notfound
        code = random.randint(20000, 99999)
        add1 = VerificationCodes(
            user_id=user.user_id,
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
            db.query(Users)
            .filter(
                or_(
                    Users.phone_number == phonenumber.lower().strip(),
                    Users.email == phonenumber.lower().strip(),
                )
            )
            .first()
        )
        if not user:
            return r.user_notfound

        code = random.randint(20000, 99999)
        add1 = VerificationCodes(
            user_id=user.user_id,
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
        user = db.query(Users).filter(Users.email == email).first()

        if user is None:
            return r.user_notfound

        ver_code = (
            db.query(VerificationCodes)
            .filter(
                VerificationCodes.user_id == user.user_id,
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
                    "user_id": user.user_id,
                    "full_name": f"{user.first_name} {user.last_name}",
                },
            }
    except Exception as e:
        print(e.args)
        return r.error_occured


def verify_signup_phone_number(phone_number: str, code: str, db: Session):
    try:
        phonenumber = phone_number

        user = db.query(Users).filter(Users.phone_number == phonenumber).first()

        if user is None:
            return r.user_notfound

        ver_code = (
            db.query(VerificationCodes)
            .filter(
                VerificationCodes.user_id == user.user_id,
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
    username: str,
    password: str,
    db: Session,
):
    try:

        login = UserHelper(db).login_user(username.lower(), password)
        if login["code"] == 404:
            return r.user_notfound
        elif login["code"] == 400:
            return r.invalid_login
        elif login["code"] == 413:
            return r.email_notverified
        elif login["code"] == 414:
            return r.phone_notverified

        else:
            user = login['user']
            access_token = create_access_token({"id": user.user_id, "email": user.email})
            refresh_token = create_refresh_token({"id": user.user_id, "email": user.email})
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
        user = db.query(Users).filter(Users.email == email.lower().strip()).first()
        if user is None:
            return r.user_notfound
        code = random.randint(20000, 99999)
        add1 = VerificationCodes(
            user_id=user.user_id,
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
        user = db.query(Users).filter(Users.email == email.lower().strip()).first()

        if user is None:
            return r.user_notfound

        ver_code = (
            db.query(VerificationCodes)
            .filter(
                VerificationCodes.user_id == user.user_id,
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
            if UserHelper(db, user.user_id).setUserPassword(new_password):
                user.updated_at = datetime.now(tz)
                db.delete(ver_code)
                db.commit()

                return {
                    "code": 200,
                    "message": "Password reset successfully",
                    "success": True,
                    "data": {"user_id": user.user_id},
                }

            return r.password_notset
    except Exception as e:
        print(e.args)
        return r.error_occured
