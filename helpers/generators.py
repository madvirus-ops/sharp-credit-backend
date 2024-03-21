import sys

sys.path.append("./")
import secrets
from datetime import datetime

from connections.database import TZ as tz


def GenerateTransactionID():
    phrase = secrets.token_hex(4).upper()
    year = datetime.now(tz).year
    day = datetime.now(tz).day
    month = datetime.now(tz).month
    sec = datetime.now(tz).second
    millisec = datetime.now(tz).microsecond
    return f"SHC-{phrase}{year}{month}"
