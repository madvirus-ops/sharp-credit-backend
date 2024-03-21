import sys

sys.path.append("./")
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, BadSignature
import logging
import os
from dotenv import load_dotenv
from connections.models import Users
from connections.database import get_db
from sqlalchemy.orm import Session
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pytz

load_dotenv()
from response import responses as r
from jose import ExpiredSignatureError, jwt, JWTError
from datetime import timedelta, datetime
from typing import Optional


LOGGER = logging.getLogger(__name__)

# AUTHENTICATION
ITS_DANGEROUS_TOKEN_KEY = os.getenv("ITS_DANGEROUS_TOKEN_KEY")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 60 * 7
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 60 * 7 * 3

token_signer = URLSafeTimedSerializer(secret_key=ITS_DANGEROUS_TOKEN_KEY)


def sign_token(jwt_token: str) -> str:
    return token_signer.dumps(obj=jwt_token)


def resolve_token(signed_token: str, max_age: int):
    """
    Takes in a signed token and resolves it with respect to time
    """
    try:
        return token_signer.loads(s=signed_token, max_age=max_age)
    except (BadTimeSignature, BadSignature) as e:
        LOGGER.exception(e)
        raise Exception


def create_access_token(data: dict):
    """
    Create A JWT
    """
    expire = timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES) + datetime.utcnow()
    data.update({"exp": expire})
    token = jwt.encode(claims=data, key=SECRET_KEY, algorithm=ALGORITHM)
    return {"code": 200, "token": token, "expires": ACCESS_TOKEN_EXPIRE_MINUTES}


def create_refresh_token(data: dict):
    """
    Create A Long Lived JWT

    """
    expire = timedelta(seconds=REFRESH_TOKEN_EXPIRE_MINUTES) + datetime.utcnow()
    data.update({"exp": expire})
    token = jwt.encode(claims=data, key=REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return {"code": 200, "token": token, "expires": REFRESH_TOKEN_EXPIRE_MINUTES}


def verify_access_token(token: str):
    """
    access JWT Decoder

    """

    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("id")
        exp = payload.get("exp")
        if id is None:
            LOGGER.error(f"Decrypted JWT has no id in payload. {payload}")
            # raise the HTTP Exception
            return {"code": 400}
        if datetime.now().replace(tzinfo=pytz.UTC) > exp.replace(tzinfo=pytz.UTC):
            return {"code": 402}

        token_uid = {"id": id, "code": 200}
    except (JWTError, ExpiredSignatureError) as e:
        LOGGER.exception(e)
        LOGGER.error("JWT Decryption Error")
        return r.error_occured

    return token_uid


def verify_refresh_token(token: str):
    """
    refresh JWT Decoder
    """
    try:
        payload = jwt.decode(token=token, key=REFRESH_SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("id")
        exp = payload.get("exp")
        if id is None:
            return {"code": 400}

        if datetime.now().replace(tzinfo=pytz.UTC) > exp.replace(tzinfo=pytz.UTC):
            return {"code": 402}

        token_id = id
    except (JWTError, ExpiredSignatureError) as e:
        LOGGER.exception(e)
        return r.error_occured
    return {"code": 200, "key": token_id}


class JWTHeader(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTHeader, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTHeader, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        ValidToken: bool = False

        try:
            payload = verify_access_token(jwtoken)
        except:
            payload = None
        if payload:
            ValidToken = True
        return ValidToken


def api_key_header(token: str = Depends(JWTHeader()), db: Session = Depends(get_db)):
    try:
        tokens = verify_access_token(token)

        if tokens["code"] != 200:
            return {
                "code": 401,
                "status": "error",
                "message": "Invalid authorization token or token Expired.",
            }

        user = db.query(Users).filter(Users.user_id == tokens["id"]).first()
        if user.account_deleted:
            return {
                "code": 401,
                "status": "error",
                "message": "User Not Found",
            }

        if user.is_restricted:
            return {
                "code": 401,
                "status": "error",
                "message": "Your account is suspended, please contact support",
            }

        return {"data": user, "code": 200, "message": "User Authenticated"}
    except Exception as e:
        print(e.args)
        return r.error_occured
