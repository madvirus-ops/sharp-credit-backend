import sys

sys.path.append("./")

import hashlib
import json
import random
import time
from pprint import pprint

import requests
from sqlalchemy.orm import Session

from connections.models import RemitaRequests, get_env
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

        payload = json.dumps(
            {
                "authorisationCode": authorisationCode,
                "phoneNumber": phone_number,
                "authorisationChannel": "USSD",
            }
        )
        response = requests.post(url, data=payload, headers=headers)
        response_data = response.json()
        if response_data["status"] == "success":
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
                RemitaRequests(
                    customer_id=customer_id,
                    response_body=json.dumps(data),
                    salary_history=json.dumps(salary_history),
                    loan_history=json.dumps(loan_history),
                    salary_count=salary_count,
                    response_id=response_id,
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

        payload = json.dumps(
            {
                "authorisationCode": authorisationCode,
                "accountNumber": account_number,
                "bankCode": bank_code,
                "authorisationChannel": "USSD",
            }
        )
        response = requests.post(url, data=payload, headers=headers)
        response_data = response.json()
        print(response_data)
        if response_data["status"] == "success":
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
                RemitaRequests(
                    customer_id=customer_id,
                    response_body=json.dumps(data),
                    salary_history=json.dumps(salary_history),
                    loan_history=json.dumps(loan_history),
                    salary_count=salary_count,
                    response_id=response_id,
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
