import sys

sys.path.append("./")

from datetime import date, datetime, timedelta

import pytz
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from connections.models import Users, VerificationCodes
from helpers.users import UserHelper
from response import responses as r


def get_user_details(user_id: str, db: Session):
    try:
        help = UserHelper(db, user_id).get_user_details()
        if help != False:
            return {
                "success": True,
                "code": 200,
                "message": "details fetched successfully",
                "data": help,
            }
        return r.error_occured
    except Exception as e:
        print(e.args)
        return r.error_occured


def change_password(user_id: str, old_password: str, new_password: str, db: Session):
    try:
        user_help = UserHelper(db, user_id)
        reset = user_help.changePassword(old_password, new_password)
        if reset["code"] == 404:
            return r.password_not_match
        elif reset["code"] == 200:
            return r.passwordset
        return r.error_occured
    except Exception as e:
        print(e.args)
        return r.error_occured
