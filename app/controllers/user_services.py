import sys

sys.path.append("./")

from datetime import date, datetime, timedelta

import pytz
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from connections.models import Users, VerificationCodes, RemitaRequests
from remita.helpers import getCustomerByAccount
from helpers.users import UserHelper
from response import responses as r
import json


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


def get_customer_loan_from_account(
    user_id: str, bank_code: str, account_number: str, db: Session
):
    try:
        request = (
            db.query(RemitaRequests)
            .filter(
                RemitaRequests.user_id == user_id,
                RemitaRequests.request_type == "phone_number",
            )
            .order_by(desc(RemitaRequests.created_at))
            .first()
        )
        if request:
            data = json.loads(request.response_body)
            customer_name = data["customerName"].split(" ")
            first_name = customer_name[0]
            last_name = customer_name[-1]
            bvn = data["bvn"]
            loan_history = json.loads(request.loan_history)
            salary_history = json.loads(request.salary_history)
            salary_count = request.salary_count
        else:
            request = getCustomerByAccount(bank_code, account_number, db)
            if request["code"] != 200:
                return r.error_occured

            first_name = request["first_name"]
            last_name = request["last_name"]
            bvn = request["bvn"]
            response_id = request["response_id"]
            salary_count = request["salary_count"]
            loan_history = request["load_history"]
            salary_history = request["salary_history"]

            update_request = (
                db.query(RemitaRequests)
                .filter(RemitaRequests.response_id == response_id)
                .first()
            )

        # TODO implementing the loan the user can get from their salary

        pass

    except Exception as e:
        print(e.args)
        return r.error_occured
