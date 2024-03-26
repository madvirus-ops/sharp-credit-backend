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
    Enum,
)
from sqlalchemy.orm import relationship

from .database import TZ, AbstractModel, get_env
import uuid

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

    loan_request = relationship(
        "LoanRequest",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Borrower.borrower_id==LoanRequest.borrower_id",
        foreign_keys="[LoanRequest.borrower_id]",
    )
    loans = relationship(
        "Loans",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Borrower.borrower_id==Loans.borrower_id",
        foreign_keys="[Loans.borrower_id]",
    )
    mandate_reference_request = relationship(
        "MandateReferenceRequests",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Borrower.borrower_id==MandateReferenceRequests.borrower_id",
        foreign_keys="[MandateReferenceRequests.borrower_id]",
    )
    stop_loan_request = relationship(
        "StopLoanRequest",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Borrower.borrower_id==StopLoanRequest.borrower_id",
        foreign_keys="[StopLoanRequest.borrower_id]",
    )
    payment = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Borrower.borrower_id==Payment.borrower_id",
        foreign_keys="[Payment.borrower_id]",
    )


class VerificationCodes(AbstractModel):
    __tablename__ = "verification_codes"

    borrower_id = Column(
        String(255),
        ForeignKey("Borrower.borrower_id", ondelete="CASCADE"),
        nullable=False,
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
        String(255),
        ForeignKey("Borrower.borrower_id", ondelete="CASCADE"),
        nullable=True,
    )
    request_payload = Column(Text, default="")

    response_body = Column(Text, default="")
    request_type = Column(String(255), default="")
    salary_history = Column(Text, default="")
    loan_history = Column(Text, default="")

    salary_count = Column(Integer, default=0)

    request_time = Column(DateTime, server_default=datetime.now())
    response_time = Column(DateTime, server_default=datetime.now())

    user = relationship(
        "Borrower", back_populates="salary_request", foreign_keys=[borrower_id]
    )


class LoanRequest(AbstractModel):
    __tablename__ = "loan_request"

    response_id = Column(String(255), default="")
    request_id = Column(String(255), default="")

    borrower_id = Column(
        String(255),
        ForeignKey("Borrower.borrower_id", ondelete="CASCADE"),
        nullable=False,
    )
    request_payload = Column(Text, default="")

    response_body = Column(Text, default="")

    loan_id = Column(String(255), default="")

    remita_account_number = Column(String(255), default="")

    status = Column(
        String(255), default="eligibility"
    )  # values: eligibility,approval,confirmation,mandate_reference,payment_failure,payment_success,payment_retrial

    reason = Column(String(255), default="")  # response from payment

    user = relationship(
        "Borrower", back_populates="loan_request", foreign_keys=[borrower_id]
    )


class MandateReferenceRequests(AbstractModel):
    __tablename__ = "mandate_reference_request"

    response_id = Column(String(255), default="")
    request_id = Column(String(255), default="")

    borrower_id = Column(
        String(255),
        ForeignKey("Borrower.borrower_id", ondelete="CASCADE"),
        nullable=True,
    )
    mandate_reference = Column(String(255), unique=True)
    request_payload = Column(Text, default="")

    response_body = Column(Text, default="")

    request_time = Column(DateTime, server_default=datetime.now())
    response_time = Column(DateTime, server_default=datetime.now())

    user = relationship(
        "Borrower",
        back_populates="mandate_reference_request",
        foreign_keys=[borrower_id],
    )


class Loans(AbstractModel):
    __tablename__ = "loans"

    borrower_id = Column(
        String(255),
        ForeignKey("Borrower.borrower_id", ondelete="CASCADE"),
        nullable=True,
    )

    loan_amount = Column(Numeric, default=0)
    outstanding_amount = Column(Numeric, default=0)
    processing_fee = Column(Numeric, default=0)

    mandate_reference = Column(String(255), default="")

    status = Column(String(255), default="pending")  # pending,active closed
    duration = Column(Integer, default=0)  # in months

    repayment_frequency = Column(String(255), default="")

    loan_disbursement_date = Column(DateTime, default=datetime.now())
    loan_due_date = Column(DateTime, default=datetime.now())
    last_repayment_date = Column(DateTime, default=datetime.now())

    user = relationship("Borrower", back_populates="loans", foreign_keys=[borrower_id])


class StopLoanRequest(AbstractModel):
    __tablename__ = "stop_loan_request"

    response_id = Column(String(255), default="")
    request_id = Column(String(255), default="")

    borrower_id = Column(
        String(255),
        ForeignKey("Borrower.borrower_id", ondelete="CASCADE"),
        nullable=True,
    )
    mandate_reference = Column(String(255), unique=True)
    transaction_id = Column(String(255), unique=True)
    request_payload = Column(Text, default="")

    response_body = Column(Text, default="")

    request_time = Column(DateTime, server_default=datetime.now())
    response_time = Column(DateTime, server_default=datetime.now())

    user = relationship(
        "Borrower",
        back_populates="stop_loan_request",
        foreign_keys=[borrower_id],
    )


class Payment(AbstractModel):
    __tablename__ = "payment"

    response_id = Column(String(255), default="")
    request_id = Column(String(255), default="")

    borrower_id = Column(
        String(255),
        ForeignKey("Borrower.borrower_id", ondelete="CASCADE"),
        nullable=True,
    )
    loan_id = Column(String(255), default="")
    loan_amount = Column(Numeric, default=0)
    mandate_reference = Column(String(255), unique=True)

    payment_status = Column(String, default="")  # pending,fail,success

    user = relationship(
        "Borrower",
        back_populates="stop_loan_request",
        foreign_keys=[borrower_id],
    )


class Staff(AbstractModel):
    __tablename__ = "staff"

    first_name = Column(String(255), default="")
    last_name = Column(String(255), default="")

    email = Column(String(255), nullable=True)
    phone_number = Column(String(255), default="")

    email_verified = Column(Boolean, default=False)
    phone_number_verified = Column(Boolean, default=False)
    password_set = Column(Boolean, default=False)

    designation = Column(String(255), default="")

    password = Column(String(255), default="")
    pin = Column(String(255), default="False")

    date_of_birth = Column(Date, default=datetime.now(tz).date())
    profile_picture = Column(String(255), default="")

    is_restricted = Column(Boolean, default=False)
