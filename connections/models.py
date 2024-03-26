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


class Borrower(AbstractModel):
    __tablename__ = "borrower"

    borrower_id = Column(String(255), nullable=False, unique=True, index=True)
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

    remita_customer_id = Column(String(255), default="")

    account_number = Column(String(255), default="")
    bank_code = Column(String(255), default="")

    first_payment_date = Column(Date, nullable=True)

    verification_codes = relationship(
        "VerificationCodes",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Borrower.borrower_id==VerificationCodes.borrower_id",
        foreign_keys="[VerificationCodes.borrower_id]",
    )

    salary_request = relationship(
        "SalaryRequests",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Borrower.borrower_id==SalaryRequests.borrower_id",
        foreign_keys="[SalaryRequests.borrower_id]",
    )


class VerificationCodes(AbstractModel):
    __tablename__ = "verification_codes"

    borrower_id = Column(
        String(255), ForeignKey("Borrower.borrower_id", ondelete="CASCADE"), nullable=False
    )
    code = Column(Integer, nullable=False)
    expires = Column(DateTime, nullable=False)
    user = relationship(
        "Borrower", back_populates="verification_codes", foreign_keys=[borrower_id]
    )



class SalaryRequests(AbstractModel):
    __tablename__ = "salary_request"

    response_id = Column(String(255), default="")
    request_id = Column(String(255), default="")

    borrower_id = Column(
        String(255), ForeignKey("Borrower.borrower_id", ondelete="CASCADE"), nullable=True
    )
    request_payload = Column(Text, default="")
    
    response_body = Column(Text, default="")
    request_type = Column(String(255), default="")
    salary_history = Column(Text, default="")
    loan_history = Column(Text, default="")

    salary_count = Column(Integer, default=0)

    request_time = Column(DateTime,server_default=func.now())
    response_time = Column(DateTime,server_default=func.now())

    user = relationship(
        "Borrower", back_populates="salary_request", foreign_keys=[borrower_id]
    )



# class SalaryRequests(AbstractModel):
#     __tablename__ = "salary_request"

#     response_id = Column(String(255), default="")

#     borrower_id = Column(
#         String(255), ForeignKey("Borrower.borrower_id", ondelete="CASCADE"), nullable=True
#     )
#     request_payload = Column(Text, default="")
    
#     response_body = Column(Text, default="")
#     request_type = Column(String(255), default="")  # phone_number or account_number
#     salary_history = Column(Text, default="")
#     loan_history = Column(Text, default="")

#     salary_count = Column(Integer, default=0)

#     user = relationship(
#         "Borrower", back_populates="salary_request", foreign_keys=[borrower_id]
#     )
