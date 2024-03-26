import sys

sys.path.append("./")
import re

from sqlalchemy.orm import Session

from connections.models import Borrower
from response import responses as r


def validate_phone_number(phone_number: str, db: Session):
    try:
        valid_prefixes = ["080", "090", "070", "081", "071", "091"]

        if phone_number.startswith("234"):
            phone_number = "0" + phone_number[3:]

        valid = any(phone_number.startswith(prefix) for prefix in valid_prefixes)

        if not valid or len(phone_number) < 11:
            return r.invalid_phone

        Borrower = (
            db.query(Borrower).filter(Borrower.phone_number == phone_number).first()
        )

        if Borrower is None:
            return {
                "success": True,
                "code": 200,
                "message": "Phone number is valid",
                "phone_number": phone_number,
            }
        elif Borrower.phone_number_verified == True:
            return r.user_exist_phone
        else:
            return {
                "success": True,
                "code": 201,
                "message": "Phone number is valid",
                "phonenumber": phone_number,
            }
    except Exception as e:
        print(e.args)
        return r.error_occured


def validate_email(email, db: Session):
    try:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        chek = re.match(pattern, email)

        if chek is None:
            return r.invalid_email

        Borrower = db.query(Borrower).filter(Borrower.email == email.lower()).first()

        if Borrower is None:
            return {
                "success": True,
                "code": 200,
                "message": "email is valid",
                "email": email,
            }
        elif Borrower.email_verified == True:
            return r.user_exist_email

        else:
            return {
                "success": True,
                "code": 201,
                "message": "email is valid",
                "email": email,
            }

    except Exception as e:
        print(e.args)
        return r.error_occured
