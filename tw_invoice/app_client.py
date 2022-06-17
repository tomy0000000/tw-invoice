import hashlib
import hmac
import re
from base64 import b64encode
from datetime import date
from random import randrange
from time import time
from typing import Optional
from urllib.parse import urlencode, urljoin
from uuid import uuid4

from requests import Session


class AppAPIClient(object):

    BASE_URL = "https://api.einvoice.nat.gov.tw"
    PATHS = {
        "invapp": "/PB2CAPIVAN/invapp/InvApp",
        "lovecode": "/PB2CAPIVAN/loveCodeapp/qryLoveCode",
        "invserv": "/PB2CAPIVAN/invServ/InvServ",
        "donate": "/PB2CAPIVAN/CarInv/Donate",
        "carrier": "/PB2CAPIVAN/Carrier/Aggregate",
    }

    def __init__(self, app_id: str, api_key: str, uuid: Optional[str] = None):
        self.app_id = app_id
        self.api_key = api_key
        self.uuid = uuid if uuid else str(uuid4())
        self.serial = 1
        self.session = Session()
        self.session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"}
        )

    def _sign(self, data: dict) -> str:
        """Generate signature"""
        data_pairs = [(name, value) for name, value in data.items() if value]
        data_pairs.sort(key=lambda x: x[0])
        query_string = urlencode(
            data_pairs, quote_via=lambda k, safe, encoding, errors: k
        )
        signature = b64encode(
            hmac.new(
                key=self.api_key.encode("utf-8"),
                msg=query_string.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).digest()
        ).decode("utf-8")
        return signature

    def get_lottery_numbers(self, invoice_term: str) -> dict:
        """查詢中獎發票號碼清單 v0.2"""
        URL = urljoin(self.BASE_URL, self.PATHS["invapp"])
        VERSION = 0.2
        if not re.match(r"^\d{3}(02|04|06|08|10|12)$", invoice_term):
            raise ValueError(f"Invalid invoice_term: {invoice_term}")
        data = {
            "version": VERSION,
            "action": "QryWinningList",
            "invTerm": invoice_term,
            "UUID": self.uuid,
            "appID": self.app_id,
        }
        return self.session.post(URL, data=data).json()

    def get_invoice_header(self, type: str, invoice_number: str, invoice_date: date):
        """查詢發票表頭"""
        URL = urljoin(self.BASE_URL, self.PATHS["invapp"])
        VERSION = 0.5
        if type not in ("QRCode", "Barcode"):
            raise ValueError("Type must be 'QRCode' or 'Barcode'")
        if not re.match(r"^[[:upper:]]{2}\d{8}$", invoice_number):
            raise ValueError(f"Invalid invoice number: {invoice_number}")
        data = {
            "version": VERSION,
            "type": type,
            "invNum": invoice_number,
            "action": "qryInvHeader",
            "generation": "V2",
            "invDate": invoice_date.strftime("%Y/%m/%d"),
            "UUID": self.uuid,
            "appID": self.app_id,
        }
        return self.session.post(URL, data=data).json()

    def get_invoice_detail(
        self,
        type: str,
        invoice_number: str,
        invoice_date: date,
        invoice_term: Optional[str] = None,
        invoice_encrypt: Optional[str] = None,
        seller_id: Optional[str] = None,
    ):
        """查詢發票明細"""
        URL = urljoin(self.BASE_URL, self.PATHS["invapp"])
        VERSION = 0.5
        if type == "QRCode":
            if not invoice_encrypt:
                raise ValueError("invoice_encrypt is required when type is QRCode")
            if not seller_id:
                raise ValueError("seller_id is required when type is QRCode")
        elif type == "Barcode":
            if not invoice_term:
                raise ValueError("invoice_term is required when type is Barcode")
        else:
            raise ValueError("Type must be 'QRCode' or 'Barcode'")
        if not re.match(r"^[[:upper:]]{2}\d{8}$", invoice_number):
            raise ValueError(f"Invalid invoice number: {invoice_number}")
        if invoice_term and not re.match(r"^\d{3}(02|04|06|08|10|12)$", invoice_term):
            raise ValueError(f"Invalid invoice_term: {invoice_term}")
        data = {
            "version": VERSION,
            "type": type,
            "invNum": invoice_number,
            "action": "qryInvDetail",
            "generation": "V2",
            "invTerm": invoice_term,
            "invDate": invoice_date.strftime("%Y/%m/%d"),
            "encrypt": invoice_encrypt if invoice_encrypt else None,
            "sellerID": seller_id if seller_id else None,
            "UUID": self.uuid,
            "random": f"{randrange(10001):0>4}",
            "appID": self.app_id,
        }
        return self.session.post(URL, data=data).json()

    def get_love_code(self, query: str) -> dict:
        """捐贈碼查詢 v0.2"""
        URL = urljoin(self.BASE_URL, self.PATHS["lovecode"])
        VERSION = 0.2
        data = {
            "version": VERSION,
            "qKey": query,
            "action": "qryLoveCode",
            "UUID": self.uuid,
            "appID": self.app_id,
        }
        return self.session.post(URL, data=data).json()

    def get_carrier_invoices_header(
        self,
        card_type: str,
        card_number: str,
        start_date: date,
        end_date: date,
        card_encrypt: str,
        only_winning: bool = False,
    ):
        """載具發票表頭查詢 v0.5"""
        URL = urljoin(self.BASE_URL, self.PATHS["invserv"])
        VERSION = 0.5
        data = {
            "version": VERSION,
            "cardType": card_type,
            "cardNo": card_number,
            "expTimeStamp": "2147483647",
            "action": "carrierInvChk",
            "timeStamp": int(time()),
            "startDate": start_date.strftime("%Y/%m/%d"),
            "endDate": end_date.strftime("%Y/%m/%d"),
            "onlyWinningInv": "Y" if only_winning else "N",
            "uuid": self.uuid,
            "appID": self.app_id,
            "cardEncrypt": card_encrypt,
        }
        return self.session.post(URL, data=data).json()

    def get_carrier_invoices_detail(
        self,
        card_type: str,
        card_number: str,
        invoice_number: str,
        invoice_date: date,
        card_encrypt: str,
        seller_name: Optional[str] = None,
        amount: Optional[int] = None,
    ):
        """載具發票明細查詢 v0.5"""
        URL = urljoin(self.BASE_URL, self.PATHS["invserv"])
        VERSION = 0.5
        if not re.match(r"^[[:upper:]]{2}\d{8}$", invoice_number):
            raise ValueError(f"Invalid invoice number: {invoice_number}")
        data = {
            "version": VERSION,
            "cardType": card_type,
            "cardNo": card_number,
            "expTimeStamp": "2147483647",
            "action": "carrierInvDetail",
            "timeStamp": int(time()),
            "invNum": invoice_number,
            "invDate": invoice_date.strftime("%Y/%m/%d"),
            "uuid": self.uuid,
            "sellerName": seller_name if seller_name else None,
            "amount": amount if amount else None,
            "appID": self.app_id,
            "cardEncrypt": card_encrypt,
        }
        return self.session.post(URL, data=data).json()

    def carrier_donate_invoice(
        self,
        card_type: str,
        card_number: str,
        invoice_date: date,
        invoice_number: str,
        love_code: str,
        card_encrypt: str,
    ):
        """載具發票捐贈 v0.1"""
        URL = urljoin(self.BASE_URL, self.PATHS["donate"])
        VERSION = 0.1
        if not re.match(r"^[[:upper:]]{2}\d{8}$", invoice_number):
            raise ValueError(f"Invalid invoice number: {invoice_number}")
        data = {
            "version": VERSION,
            "serial": f"{self.serial:0>10}",
            "cardType": card_type,
            "cardNo": card_number,
            "expTimeStamp": "2147483647",
            "action": "carrierInvDnt",
            "timeStamp": int(time()),
            "invDate": invoice_date.strftime("%Y/%m/%d"),
            "invNum": invoice_number,
            "npoBan": love_code,
            "uuid": self.uuid,
            "appID": self.app_id,
            "cardEncrypt": card_encrypt,
        }
        signature = self._sign(data)
        data["signature"] = signature
        self.serial += 1
        return self.session.post(URL, data=data).json()

    def get_aggregate_carrier(
        self,
        card_type: str,
        card_number: str,
        card_encrypt: str,
    ):
        """手機條碼歸戶載具查詢 v1.0"""
        URL = urljoin(self.BASE_URL, self.PATHS["carrier"])
        VERSION = 1.0
        data = {
            "version": VERSION,
            "serial": f"{self.serial:0>10}",
            "action": "qryCarrierAgg",
            "cardType": card_type,
            "cardNo": card_number,
            "cardEncrypt": card_encrypt,
            "appID": self.app_id,
            "timeStamp": int(time()),
            "uuid": self.uuid,
        }
        signature = self._sign(data)
        data["signature"] = signature
        self.serial += 1
        return self.session.post(URL, data=data).json()
