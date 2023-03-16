import logging
import time
import math
import base64
import requests

from datetime import datetime
from requests.auth import HTTPBasicAuth
from requests import Response

from mpesa_integration.settings import env
from .models import *
from .exceptions import *

logging = logging.getLogger("default")

now = datetime.now()

class MpesaResponse(Response):
	response_description = ""
	error_code = None
	error_message = ''


def mpesa_response(r):
	"""
	Create MpesaResponse object from requests.Response object
	
	Arguments:
		r (requests.Response) -- The response to convert
	"""

	r.__class__ = MpesaResponse
	json_response = r.json()
	r.response_description = json_response.get('ResponseDescription', '')
	r.error_code = json_response.get('errorCode')
	r.error_message = json_response.get('errorMessage', '')
	return r



class MpesaGateWay:
    business_shortcode = None
    consumer_key = None
    consumer_secret = None
    access_token_url = None
    access_token = None
    access_token_expiration = None
    checkout_url = None
    timestamp = None


    def __init__(self):
        now = datetime.now()
        self.business_shortcode = env("business_shortcode")
        self.consumer_key = env("consumer_key")
        self.consumer_secret = env("consumer_secret")
        self.access_token_url = env("access_token_url")
    
        self.password = self.generate_password()
        self.checkout_url = env("checkout_url")

        try:
            self.access_token = self.getAccessToken()
            
            if self.access_token is None:
                raise Exception("Request for access token failed.")
        except Exception as e:
            logging.error("Error {}".format(e))
            #print("Hellen")
        else:
            self.access_token_expiration = time.time() + 340000000000000000

    def getAccessToken(self):
        try:
            res = requests.get(self.access_token_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
            print(res)
        except Exception as err:
            logging.error("Error {}".format(err))
            #raise err
        else:
            token = res.json()["access_token"]
            self.headers = {"Authorization": "Bearer %s" % token}
            return token

    class Decorators:
        @staticmethod
        def refreshToken(decorated):
            def wrapper(gateway, *args, **kwargs):
                if (gateway.access_token_expiration and time.time() > gateway.access_token_expiration):
                    token = gateway.getAccessToken()
                    gateway.access_token = token
                return decorated(gateway, *args, **kwargs)

            return wrapper


    def generate_password(self):
        """Generates mpesa api password using the provided shortcode and passkey"""
        self.timestamp = now.strftime("%Y%m%d%H%M%S")
        password_str = env("business_shortcode") + env("pass_key") + self.timestamp
        password_bytes = password_str.encode("ascii")
        return base64.b64encode(password_bytes).decode("utf-8")

    @Decorators.refreshToken
    def stk_push(self, phone_number, amount, callback_url, account_reference, transaction_desc):
        if str(account_reference).strip() == '':
            raise MpesaInvalidParameterException('Account reference cannot be blank')
        if str(transaction_desc).strip() == '':
            raise MpesaInvalidParameterException('Transaction description cannot be blank')
        if not isinstance(amount, int):
            raise MpesaInvalidParameterException('Amount must be an integer')

        
        phone_number = phone_number
        business_shortcode = self.business_shortcode
        timestamp = self.timestamp
        password = self.password
        
        
        req_data = {
            "BusinessShortCode": business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
            
        }

        try:
            res = requests.post(self.checkout_url, json=req_data, headers=self.headers, timeout=30)
            response = mpesa_response(res)

            return response
        except requests.exceptions.ConnectionError:
            raise MpesaConnectionError('Connection failed')
        except Exception as ex:
            raise MpesaConnectionError(str(ex))
    """
        logging.info("Mpesa request data {}".format(req_data))
        logging.info("Mpesa response info {}".format(res_data))

        if res.ok:
            data["checkout_request_id"] = res_data["CheckoutRequestID"]

            Transaction.objects.create(**data)
        print(self.headers)
        return res_data
    
    def check_status(self, data):
        try:
            status = data["Body"]["stkCallback"]["ResultCode"]
        except Exception as e:
            logging.error(f"Error: {e}")
            status = 1
        return status

    def get_transaction_object(data):
        checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
        transaction, _ = Transaction.objects.get_or_create(
            checkout_request_id=checkout_request_id
        )

        return transaction

    def handle_successful_pay(self, data, transaction):
        items = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]
        for item in items:
            if item["Name"] == "Amount":
                amount = item["Value"]
            elif item["Name"] == "MpesaReceiptNumber":
                receipt_no = item["Value"]
            elif item["Name"] == "PhoneNumber":
                phone_number = item["Value"]

        transaction.amount = amount
        transaction.phone_number = PhoneNumber(raw_input=phone_number)
        transaction.receipt_no = receipt_no
        transaction.confirmed = True

        return transaction

    def callback_handler(self, data):
        status = self.check_status(data)
        transaction = self.get_transaction_object(data)
        if status==0:
            self.handle_successful_pay(data, transaction)
        else:
            transaction.status = 1

        transaction.status = status
        transaction.save()

        transaction_data = TransactionSerializer(transaction).data

        logging.info("Transaction completed info {}".format(transaction_data))

        return Response({"status": "ok", "code": 0}, status=200)

        """