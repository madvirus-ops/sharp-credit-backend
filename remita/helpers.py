import sys

sys.path.append("./")

from connections.models import RemitaRequests, get_env
from helpers.generators import GenerateTransactionID
import requests
from response import responses as r
import json
from sqlalchemy.orm import Session


BASE_URL = get_env("REMITA_BASE_URL")
API_KEY = get_env("REMITA_API_KEY")
MERCHANT_ID = get_env("REMITA_MERCHANT_ID")
REQUEST_ID = get_env("REMITA_REQUEST_ID")
CONSUMER_KEY = get_env("REMITA_CONSUMER_KEY")
CONSUMER_TOKEN = get_env("REMITA_CONSUMER_TOKEN")

GENERAL_HEADERS = {
    "Content-Type": "application/json",
    "Content-Type": "application/json",
    "Api_Key": API_KEY,
    "Merchant_id": MERCHANT_ID,
    "Request_id": "",
    "Authorization": f"remitaConsumerKey={CONSUMER_KEY}, remitaConsumerToken={CONSUMER_TOKEN}",
}


def getCustomerByPhonenumber(phone_number: str, db: Session):
    try:
        url = f"{BASE_URL}/payday/salary/history/ph"

        headers = GENERAL_HEADERS
        REQUEST_ID = GenerateTransactionID()
        headers["Request_id"] = REQUEST_ID
        payload = json.dumps(
            {
                "authorisationCode": "randomnumber",
                "phoneNumber": phone_number,
                "authorisationChannel": "USSD",
            }
        )
        response = requests.post(url, data=payload, headers=headers)
        response_data = response.json()
        if response_data["status"] == "success":
            data = response_data["data"]

            response_id = REQUEST_ID
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
