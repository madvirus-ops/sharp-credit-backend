import sys
from datetime import datetime

import pytz
from sqlalchemy import desc, or_

sys.path.append("./")
import decimal
import random
import secrets
import uuid

from passlib.context import CryptContext
from sqlalchemy.orm import Session

import response.responses as r
from connections.models import Borrower

pwd_hash = CryptContext(schemes=["bcrypt"], deprecated="auto")


tz = pytz.timezone("Africa/Lagos")


class UserHelper(object):
    """Helper class for user related functions"""

    def __init__(self, db: Session, borrower_id: str = ""):
        self.db = db
        self.borrower_id = borrower_id

    def hash_pin(self, pin):
        return pwd_hash.hash(pin)

    def verify_pin(self, pin, hashed_pin):
        return pwd_hash.verify(secret=pin, hash=hashed_pin)

    def createUser(
        self,
        first_name: str,
        last_name: str,
        phone_number: str,
        email: str,
        password: str = "",
    ):
        try:
            user = (
                self.db.query(Borrower)
                .filter(Borrower.phone_number == phone_number)
                .first()
            )

            if user is not None:
                return {
                    "code": 400,
                    "success": False,
                    "message": "account already exists",
                }

            user = Borrower(
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                email=email.strip(),
                borrower_id=self.borrower_id,
                phone_number=phone_number.strip(),
                password=self.hash_pin(password),
            )
            self.db.add(user)
            self.db.commit()
            return {"code": 200, "borrower_id": self.borrower_id}
        except Exception as e:
            print(e.args)
            print("error here \n\n")
            return r.error_occured

    def login_user(self, phone_number: str, password: str):
        try:
            user = (
                self.db.query(Borrower)
                .filter(
                    or_(
                        Borrower.phone_number == phone_number,
                        Borrower.username == phone_number,
                    )
                )
                .first()
            )

            if not user or user.account_deleted:
                return {"code": 404, "message": "user not found"}
            # if not user or not user.email_verified:
            #     return {"code": 413, "message": "user not found"}
            if not user or not user.phone_number_verified:
                return {"code": 414, "message": "Account not verified"}

            if self.verify_pin(password, user.password):
                user.last_login = datetime.now(tz)
                self.db.commit()
                return {"code": 200, "status": "success", "user": user}

            return {"code": 400, "message": "invalid password"}

        except Exception as e:
            print(e.args)
            # raise e
            return {"code": 400, "message": "error occured"}

    def get_user_by_id(self):
        try:
            user = (
                self.db.query(Borrower)
                .filter(Borrower.borrower_id == self.borrower_id)
                .first()
            )
            return user
        except Exception as e:
            raise e

    def get_user_by_username(self, username):
        try:
            user = self.db.query(Borrower).filter(Borrower.username == username).first()
            return user
        except Exception as e:
            return None

    def get_user_details(self):
        try:
            user = self.get_user_by_id()

            data = {
                "borrower_id": user.borrower_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "username": user.username,
                "email": user.email,
                "date_of_birth": user.date_of_birth,
                "created_at": user.created_at,
            }
            return data
        except Exception as e:
            print(f"Error getting user full details, reason: {e.args}")
            return False

    def restrict_user(self):
        try:
            user = self.get_user_by_id()
            user.is_restricted = True
            user.updated_at = datetime.now(tz)
            self.db.commit()
            return True
        except Exception as e:
            return False

    def set_profile_image_url(self, image_url: str):
        try:
            user = self.get_user_by_id()
            user.profile_picture = image_url
            user.updated_at = datetime.now(tz)
            self.db.commit()
            return True
        except Exception as e:
            return False

    def delete_user_account(self):
        try:
            user = (
                self.db.query(Borrower)
                .filter(Borrower.borrower_id == self.borrower_id)
                .first()
            )

            user.account_deleted = True
            user.updated_at = datetime.now(tz)
            self.db.commit()

            return True
        except Exception as e:
            return False

    def deactivate_user_account(self):
        try:
            user = self.get_user_by_id()
            user.account_deleted = True
            user.updated_at = datetime.now(tz)
            self.db.commit()
            return True
        except Exception as e:
            return False

    def setUserPin(self, pin: str):
        try:
            user = self.get_user_by_id()
            user.pin = self.hash_pin(pin)
            user.updated_at = datetime.now(tz)
            self.db.commit()
            return True
        except Exception as e:
            return False

    def setUserPassword(self, password: str):
        try:
            user = self.get_user_by_id()
            user.password = self.hash_pin(password)
            user.updated_at = datetime.now(tz)
            self.db.commit()
            return True
        except Exception as e:
            return False

    def changePassword(self, old_password, new_password):
        try:
            user = self.get_user_by_id()
            if self.verify_pin(old_password, user.password):
                self.setUserPassword(new_password)
                return {"code": 200}
            return {"code": 404}
        except Exception as e:
            return {"code": 400}

    def changePin(self, old_pin, new_pin):
        try:
            user = self.get_user_by_id()
            if self.verify_pin(old_pin, user.pin):
                self.setUserPin(new_pin)
                return {"code": 200}
            return {"code": 404}
        except Exception as e:
            return {"code": 400}

    def setUsername(self, username: str):
        try:
            exist = self.get_user_by_username(username)
            if exist is None:
                user = self.get_user_by_id()
                user.username = username.lower()
                self.db.commit()
                return {"code": 200}
            return {"code": 419}
        except Exception as e:
            return {"code": 400}
