import sys
sys.path.append("./")

from sqlalchemy import (
    Column,
    DateTime,
    Time,
    Boolean,
    Integer,
    String,
    Text,
    Numeric,
    ForeignKey,
    Date,
    asc,
    desc,
    func,
)
from datetime import datetime
from sqlalchemy.orm import relationship
from .database import AbstractModel, TZ, get_env

tz = TZ


class Users(AbstractModel):
    __tablename__ = "users"

    user_id = Column(String(255), nullable=False, unique=True, index=True)
    first_name = Column(String(255), default="")
    last_name = Column(String(255), default="")
    username = Column(String(255), default="")
    
    email = Column(String(255), nullable=True)
    phone_number = Column(String(255), default="")

    email_verified = Column(Boolean,default=False)
    phone_number_verified = Column(Boolean,default=False)

    password = Column(String(255), default="")
    pin  = Column(String(255),default="False")

    date_of_birth = Column(Date, default=datetime.now(tz).date())
    profile_picture = Column(String(255), default="")

    is_restricted = Column(Boolean,default=False)
    account_deleted = Column(Boolean,default=False)

    verification_codes = relationship(
        "VerificationCodes",
        back_populates="user",
        cascade="all, delete-orphan",
        primaryjoin="Users.user_id==VerificationCodes.user_id",
        foreign_keys="[VerificationCodes.user_id]",
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
