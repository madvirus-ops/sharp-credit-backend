import sys

sys.path.append("./")
import logging
import os
import uuid
from datetime import datetime

import pytz
from dotenv import load_dotenv
from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False, pool_size=100)


Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    ensures the database connection is always closed
    to use this we have to use fastapi.Depends() as an argument in the routes
    """
    db = SessionLocal()
    try:
        yield db

    except Exception as e:
        print(e.args)
        db.rollback()

    finally:
        db.close()


logger = logging.getLogger(__name__)


TZ = pytz.timezone("Africa/Lagos")


def get_env(value: str):
    return os.getenv(value)


class AbstractModel(Base):
    """abstract model"""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, primary_key=True)
    created_at = Column(DateTime, default=datetime.now(TZ))
    updated_at = Column(DateTime, default=datetime.now(TZ))
