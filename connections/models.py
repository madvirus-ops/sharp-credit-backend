import sys

sys.path.append("./")

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    asc,
    desc,
    func,
)
from sqlalchemy.orm import relationship

from .database import TZ, AbstractModel, get_env

tz = TZ


class Users(AbstractModel):
    __tablename__ = "users"

    user_id = Column(String(255), nullable=False, unique=True, index=True)
    first_name = Column(String(255), default="")
    last_name = Column(String(255), default="")
    username = Column(String(255), default="")

    email = Column(String(255), nullable=True)
    phone_number = Column(String(255), default="")

    email_verified = Column(Boolean, default=False)
    phone_number_verified = Column(Boolean, default=False)

    password = Column(String(255), default="")
    pin = Column(String(255), default="False")

    date_of_birth = Column(Date, default=datetime.now(tz).date())
    profile_picture = Column(String(255), default="")

    is_restricted = Column(Boolean, default=False)
    account_deleted = Column(Boolean, default=False)

    verification_codes = relationship(
        "VerificationCodes",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Users.user_id==VerificationCodes.user_id",
        foreign_keys="[VerificationCodes.user_id]",
    )

    remita_request = relationship(
        "RemitaRequests",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Users.user_id==RemitaRequests.user_id",
        foreign_keys="[RemitaRequests.user_id]",
    )


class VerificationCodes(AbstractModel):
    __tablename__ = "verification_codes"

    user_id = Column(
        String(255), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    code = Column(Integer, nullable=False)
    expires = Column(DateTime, nullable=False)
    user = relationship(
        "Users", back_populates="verification_codes", foreign_keys=[user_id]
    )


class RemitaRequests(AbstractModel):
    __tablename__ = "remita_requests"

    response_id = Column(String(255), default="")

    user_id = Column(
        String(255), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True
    )
    request_payload = Column(Text, default="")
    customer_id = Column(String(255), default="")
    response_body = Column(Text, default="")
    request_type = Column(String(255), default="")  # phone_number or account_number
    salary_history = Column(Text, default="")
    loan_history = Column(Text, default="")

    salary_count = Column(Integer, default=0)

    user = relationship(
        "Users", back_populates="remita_request", foreign_keys=[user_id]
    )
