import sys

sys.path.append("./")

import hashlib
import json
import random
import time
from pprint import pprint

import requests
from sqlalchemy.orm import Session

from connections.models import SalaryRequests, get_env, tz,LoanRequest,StopLoanRequest,MandateReferenceRequests
from datetime import datetime
from helpers.generators import GenerateTransactionID
from response import responses as r

apiToken = get_env("REMITA_API_TOKEN")
API_KEY = get_env("REMITA_API_KEY")
MERCHANT_ID = get_env("REMITA_MERCHANT_ID")
BASE_URL = get_env("REMITA_BASE_URL")


def generate_remita_auth_variables():

    requestId = str(int(time.time() * 1000))

    randomnumber = str(random.randint(0, 1101233))
    authorisationCode = randomnumber

    concatenated_string = API_KEY + requestId + apiToken

    hashed_data = hashlib.sha512(concatenated_string.encode()).hexdigest()

    apiHash = hashed_data

    authorization = f"remitaConsumerKey={API_KEY}, remitaConsumerToken={apiHash}"

    print(apiHash)

    return requestId, authorisationCode, apiHash, authorization


def getCustomerByPhonenumber(phone_number: str, db: Session):
    try:
        url = f"{BASE_URL}/payday/salary/history/ph"

        requestId, authorisationCode, apiHash, authorization = (
            generate_remita_auth_variables()
        )

        headers = {
            "Content-Type": "application/json",
            "Api_Key": API_KEY,
            "Merchant_id": MERCHANT_ID,
            "Request_id": requestId,
            "Authorization": authorization,
        }

        payload = {
            "authorisationCode": authorisationCode,
            "phoneNumber": phone_number,
            "authorisationChannel": "USSD",
        }
        request_time = datetime.now(tz)
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response_data = response.json()
        if response_data["status"] == "success":
            response_time = datetime.now(tz)
            data = response_data["data"]

            response_id = requestId
            customer_id = data["customerID"]
            bvn = data["bvn"]
            company_name = data["companyName"]

            customer_name = data["customerName"].split(" ")
            first_name = customer_name[0]
            last_name = customer_name[-1]

            category = data["category"]
            salary_count = data["salaryCount"]
            loan_history = data["loanHistoryDetails"]
            salary_history = data["salaryPaymentDetails"]

            new = db.add(
                SalaryRequests(
                    customer_id=customer_id,
                    response_body=json.dumps(data),
                    salary_history=json.dumps(salary_history),
                    loan_history=json.dumps(loan_history),
                    salary_count=salary_count,
                    request_type="phone_number",
                    response_id=response_id,
                    request_payload=json.dumps(payload),
                    request_time=request_time,
                    response_time=response_time,
                )
            )
            db.commit()

            return {
                "code": 200,
                "first_name": first_name,
                "last_name": last_name,
                "bvn": bvn,
                "response_id": response_id,
            }
        return r.error_occured

    except Exception as e:
        print(e.args)
        return r.error_occured


def getCustomerByAccount(bank_code: str, account_number: str, db: Session):
    try:
        url = f"{BASE_URL}/payday/salary/history/ph"

        requestId, authorisationCode, apiHash, authorization = (
            generate_remita_auth_variables()
        )

        headers = {
            "Content-Type": "application/json",
            "Api_Key": API_KEY,
            "Merchant_id": MERCHANT_ID,
            "Request_id": requestId,
            "Authorization": authorization,
        }

        payload = {
            "authorisationCode": authorisationCode,
            "accountNumber": account_number,
            "bankCode": bank_code,
            "authorisationChannel": "USSD",
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response_data = response.json()
        request_time = datetime.now(tz)
        # print(response_data)
        if response_data["status"] == "success":
            data = response_data["data"]
            response_time = datetime.now(tz)
            response_id = requestId
            customer_id = data["originalCustomerId"]
            bvn = data["bvn"]

            customer_name = data["customerName"].split(" ")
            first_name = customer_name[0]
            last_name = customer_name[-1]

            category = data["category"]
            salary_count = data["salaryCount"]
            loan_history = data["loanHistoryDetails"]
            salary_history = data["salaryPaymentDetails"]

            new = db.add(
                SalaryRequests(
                    customer_id=customer_id,
                    response_body=json.dumps(data),
                    salary_history=json.dumps(salary_history),
                    loan_history=json.dumps(loan_history),
                    salary_count=salary_count,
                    response_id=response_id,
                    request_type="account_number",
                    request_payload=json.dumps(payload),
                    request_time=request_time,
                    response_time=response_time,
                )
            )
            db.commit()

            return {
                "code": 200,
                "first_name": first_name,
                "last_name": last_name,
                "bvn": bvn,
                "response_id": response_id,
                "salary_count": salary_count,
                "salary_history": salary_history,
                "loan_history": loan_history,
            }
        return r.error_occured

    except Exception as e:
        print(e.args)
        return r.error_occured


# getCustomerByAccount("023", "0235012284")
# """


# BASE URL
# https://remitademo.net/remita/exapp/api/v1/send/api
# CREDENTIALS
# - merchantId: 27768931
# - apiKey: Q1dHREVNTzEyMzR8Q1dHREVNTw==
# - apiToken: SGlQekNzMEdMbjhlRUZsUzJCWk5saDB6SU14Zk15djR4WmkxaUpDTll6bGIxRCs4UkVvaGhnPT0=


# "accountNumber": "0235012284",
# "bankCode": "023",

# """

REMITA_BANK_CODES = {
    "000": "CENTRAL BANK OF NIGERIA",
    "011": "FIRST BANK OF NIGERIA PLC",
    "023": "NIGERIA INTERNATIONAL BANK (CITIBANK)",
    "030": "HERITAGE BANK PLC",
    "032": "UNION BANK OF NIGERIA PLC",
    "033": "UBA PLC",
    "035": "WEMA BANK PLC",
    "039": "STANBIC IBTC BANK PLC",
    "044": "ACCESS BANK PLC",
    "050": "ECOBANK NIGERIA PLC",
    "057": "ZENITH BANK PLC",
    "058": "GUARANTY TRUST BANK",
    "068": "STANDARD CHARTERED BANK NIGERIA LTD",
    "070": "FIDELITY BANK PLC",
    "076": "POLARIS BANK PLC",
    "101": "PROVIDUS BANK",
    "214": "FIRST CITY MONUMENT BANK PLC",
    "215": "UNITY BANK PLC",
    "232": "STERLING BANK PLC",
    "301": "JAIZ BANK",
    "459": "CORONATION MERCHANT BANK LIMITED",
    "480": "JUBILEE BANK",
    "510120013": "KANO MICROFINANCE BANKS",
    "511080016": "ESO SAVINGS LOANS PLC",
    "511080026": "ASO SAVINGS AND LOANS",
    "511080036": "NATIONAL HOUSING FUND",
    "511080106": "GAA-AKANBI MICRO FINANCE BANK",
    "512170012": "CLASSIC MICROFINANCE BANK",
    "512170022": "SOLID ROCK MFB OKE ONA ABEOKUTA",
    "512170032": "LAVENDER MICROFINANCE BANK LTD",
    "512170042": "EBIGI MICROFINANCE BANK",
    "512170052": "EFOTAMODI/OGUNOLA MICROFINANCE BANK",
    "512170062": "EIYEPE MICROFINANCE BANK",
    "512170072": "EJOSE MICROFINANCE BANK LTD",
    "512170082": "EMAZING GRACE MICROFINANCE BANK",
    "512170092": "CATLAND MICROFINANCE BANK LTD",
    "512170102": "OGUN STATE MICROFINANCE BANKS",
    "512170112": "UKUOMBE MICROFINANCE BANK LTD",
    "512170122": "URUWON MICROFINANCE BANK",
    "512170132": "USO-E MICROFINANCE BANK",
    "512170142": "EPPLE MICROFINANCE BANK",
    "512170152": "OFONYIN MICROFINANCE BANK",
    "512170162": "OMODI-IMOSAN MICROFINANCE BANK LTD",
    "512170172": "OJEBU-IFE COMMUNITY BANK NIG. LTD",
    "512170182": "OJEBU-IMUSIN MICROFINANCE BANK LTD",
    "512170192": "OKENNE MICROFINANCE BANK LTD",
    "512170202": "OGUN STATE MICROFINANCE BANKS",
    "512170212": "OLISAN MICROFINANCE BANK LTD",
    "512170222": "OMOWO MICROFINANCE BANK NIG LTD",
    "512170232": "ONTERLAND MICROFINANCE BANK",
    "512170242": "OPERU MICROFINANCE BANK LTD",
    "512170252": "OTELE MICROFINANCE BANK LTD",
    "512170262": "OGUN STATE MICROFINANCE BANKS",
    "512170272": "OGUN STATE MICROFINANCE BANKS",
    "512170282": "OGUN STATE MICROFINANCE BANKS",
    "512170292": "MALPOLY MICROFINANCE BANK",
    "512170302": "MOLUSI MICROFINANCE BANK LTD",
    "512170312": "NEW IMAGE MFB EGBA ODEDA",
    "512170322": "COMBINED BENEFITS MICROFINANCE BANK",
    "512170332": "OGUN STATE MICROFINANCE BANKS",
    "512170342": "AMU COMMUNITY BANK LTD",
    "512170352": "ARISUN MFB",
    "512170362": "RIVERSIDE MICROFINANCE BANK LTD",
    "512170372": "SAGAM MICROFINANCE BANK",
    "512170382": "TRUST MFB EGBA OWODE ABEOKUTA",
    "512170392": "OGUN STATE MICROFINANCE BANKS",
    "512170402": "ACON SUCCESS MICROFINANCE BANK LTD",
    "512170412": "UNAAB MICROFINANCE BANK",
    "512170422": "WEST-END MICROFINANCE BANK",
}


def getCustomerLoanHistory(user_id:str,db:Session):
    try:
        pass
    except Exception as e:
        print(e.args)
        return r.error_occured