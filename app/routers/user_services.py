import sys
sys.path.append("./")
from fastapi import APIRouter, BackgroundTasks, Depends, Response, Request, Header
import re
from connections.database import get_db
from connections.schemas import (
    ChangePassword,
)
from app.controllers.user_services import *
from helpers.security import api_key_header


router = APIRouter(prefix="/api/v2/user", tags=["User Section"])


@router.get("/")
async def get_full__details(
    response: Response,
    db: Session = Depends(get_db),
    authorization: str = Depends(api_key_header),
):
    response.status_code = authorization["code"]
    if authorization["code"] == 200:
        result = get_user_details(authorization["data"].user_id, db)
        response.status_code = result["code"]
        return result
    return authorization
