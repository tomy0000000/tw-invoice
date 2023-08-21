from datetime import date
from time import time
from typing import Tuple, Union
from uuid import uuid4

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from requests import Session
from requests.adapters import HTTPAdapter, Retry

from .schema import (
    AggregateCarrierResponse,
    CarrierInvoiceDonateResponse,
    CarrierInvoicesDetailResponse,
    CarrierInvoicesHeaderResponse,
    InvoiceDetailResponse,
    InvoiceHeaderResponse,
    LotteryNumberResponse,
    LoveCodeResponse,
)
from .utils import (
    build_api_url,
    check_api_error,
    sign,
    validate_invoice_number,
    validate_invoice_random,
    validate_invoice_term,
)


class AppAPIClient(object):
    def __init__(
        self,
        app_id: str,
        api_key: str,
        uuid: Union[str, None] = None,
        ts_tolerance: int = 20,
        max_retries: int = 20,
        skip_validation: bool = False,
        timeout: Union[float, Tuple[float, float], Tuple[float, None]] = (3, 1),
    ):
        self.app_id = app_id
        self.api_key = api_key
        self.uuid = str(uuid) if uuid else str(uuid4())
        if ts_tolerance < 10 or ts_tolerance > 180:
            raise ValueError("ts_tolerance must be between 10 and 180")
        self.ts_tolerance = ts_tolerance
        if not isinstance(skip_validation, bool):
            raise ValueError("skip_validation must be a boolean")
        self.skip_validation = skip_validation
        self.serial = 1
        self.session = Session()
        self.session.headers.update(
            {"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=max_retries,
                    backoff_factor=0.1,
                    allowed_methods=["POST"],
                    status_forcelist=[500, 502, 503, 504],
                    raise_on_status=False,
                )
            ),
        )
        self.timeout = timeout

    def get_lottery_numbers(
        self, invoice_term: str
    ) -> Union[LotteryNumberResponse, dict]:
        """查詢中獎發票號碼清單 v0.2"""
        URL = build_api_url("invapp")
        VERSION = 0.2
        if not validate_invoice_term(invoice_term):
            raise ValueError(f"Invalid invoice_term: {invoice_term}")
        data = {
            "version": VERSION,
            "action": "QryWinningList",
            "invTerm": invoice_term,
            "UUID": self.uuid,
            "appID": self.app_id,
        }
        results = check_api_error(
            self.session.post(URL, data=data, timeout=self.timeout)
        )
        if not self.skip_validation:
            results = LotteryNumberResponse.parse_obj(results)
        return results

    def get_invoice_header(
        self,
        barcode_type: Literal["QRCode", "Barcode"],
        invoice_number: str,
        invoice_date: date,
    ) -> Union[InvoiceHeaderResponse, dict]:
        """查詢發票表頭 v0.5"""
        URL = build_api_url("invapp")
        VERSION = 0.5
        if barcode_type not in ("QRCode", "Barcode"):
            raise ValueError("Type must be 'QRCode' or 'Barcode'")
        if not validate_invoice_number(invoice_number):
            raise ValueError(f"Invalid invoice number: {invoice_number}")
        data = {
            "version": VERSION,
            "type": barcode_type,
            "invNum": invoice_number,
            "action": "qryInvHeader",
            "generation": "V2",
            "invDate": invoice_date.strftime("%Y/%m/%d"),
            "UUID": self.uuid,
            "appID": self.app_id,
        }
        results = check_api_error(
            self.session.post(URL, data=data, timeout=self.timeout)
        )
        if not self.skip_validation:
            results = InvoiceHeaderResponse.parse_obj(results)
        return results

    def get_invoice_detail(
        self,
        barcode_type: Literal["QRCode", "Barcode"],
        invoice_number: str,
        invoice_date: date,
        invoice_random: str,
        invoice_term: Union[str, None] = None,
        invoice_encrypt: Union[str, None] = None,
        seller_id: Union[str, None] = None,
    ):
        """
        查詢發票明細 v0.6
        `invoice_random`: 錯誤將僅回傳發票表頭，正確將回傳完整明細

        `barcode_type`: "Barcode"
        `invoice_number`: 發票號碼
        `invoice_date`: 發票日期
        `invoice_random`: 發票隨機碼 (4位)
        `invoice_term`: 發票期別， 3 位民國年+ 2 位雙數月份，如：11006

        or

        `barcode_type`: "QRCode"
        `invoice_number`: 發票號碼
        `invoice_date`: 發票日期
        `invoice_random`: 發票隨機碼 (4位)
        `invoice_encrypt`: 發票檢驗碼 (左側QRCode中，24位)
        `seller_id`: 商家統編
        """
        URL = build_api_url("invapp")
        VERSION = 0.6
        if barcode_type == "QRCode":
            if not invoice_encrypt:
                raise ValueError(
                    "invoice_encrypt is required when barcode_type is QRCode"
                )
            if not isinstance(invoice_encrypt, str) or len(invoice_encrypt) != 24:
                raise ValueError("invoice_encrypt must be a string of 24 characters")
            if not seller_id:
                raise ValueError("seller_id is required when barcode_type is QRCode")
        elif barcode_type == "Barcode":
            if not invoice_term:
                raise ValueError(
                    "invoice_term is required when barcode_type is Barcode"
                )
            if not validate_invoice_term(invoice_term):
                raise ValueError(f"Invalid invoice_term: {invoice_term}")
        else:
            raise ValueError("barcode_type must be 'QRCode' or 'Barcode'")
        if not validate_invoice_number(invoice_number):
            raise ValueError(f"Invalid invoice number: {invoice_number}")
        if not validate_invoice_random(invoice_random):
            raise ValueError(f"Invalid invoice random: {invoice_random}")
        data = {
            "version": VERSION,
            "type": barcode_type,
            "invNum": invoice_number,
            "action": "qryInvDetail",
            "generation": "V2",
            "invTerm": invoice_term,
            "invDate": invoice_date.strftime("%Y/%m/%d"),
            "encrypt": invoice_encrypt,
            "sellerID": seller_id,
            "UUID": self.uuid,
            "randomNumber": invoice_random,
            "appID": self.app_id,
        }
        results = check_api_error(
            self.session.post(URL, data=data, timeout=self.timeout)
        )
        if not self.skip_validation:
            results = InvoiceDetailResponse.parse_obj(results)
        return results

    def get_love_code(self, query: str) -> dict:
        """捐贈碼查詢 v0.2"""
        URL = build_api_url("lovecode")
        VERSION = 0.2
        data = {
            "version": VERSION,
            "qKey": query,
            "action": "qryLoveCode",
            "UUID": self.uuid,
            "appID": self.app_id,
        }
        results = check_api_error(
            self.session.post(URL, data=data, timeout=self.timeout)
        )
        if not self.skip_validation:
            results = LoveCodeResponse.parse_obj(results)
        return results

    def get_carrier_invoices_header(
        self,
        card_type: str,
        card_number: str,
        start_date: date,
        end_date: date,
        card_encrypt: str,
        only_winning: bool = False,
    ) -> Union[dict, CarrierInvoicesHeaderResponse]:
        """載具發票表頭查詢 v0.5"""
        URL = build_api_url("invserv")
        VERSION = 0.5
        data = {
            "version": VERSION,
            "cardType": card_type,
            "cardNo": card_number,
            "expTimeStamp": "2147483647",
            "action": "carrierInvChk",
            "timeStamp": int(time() + self.ts_tolerance),
            "startDate": start_date.strftime("%Y/%m/%d"),
            "endDate": end_date.strftime("%Y/%m/%d"),
            "onlyWinningInv": "Y" if only_winning else "N",
            "uuid": self.uuid,
            "appID": self.app_id,
            "cardEncrypt": card_encrypt,
        }
        results = check_api_error(
            self.session.post(URL, data=data, timeout=self.timeout)
        )
        if not self.skip_validation:
            results = CarrierInvoicesHeaderResponse.parse_obj(results)
        return results

    def get_carrier_invoices_detail(
        self,
        card_type: str,
        card_number: str,
        invoice_number: str,
        invoice_date: date,
        card_encrypt: str,
        seller_name: Union[str, None] = None,
        amount: Union[int, None] = None,
    ) -> Union[dict, CarrierInvoicesDetailResponse]:
        """載具發票明細查詢 v0.5"""
        URL = build_api_url("invserv")
        VERSION = 0.5
        if not validate_invoice_number(invoice_number):
            raise ValueError(f"Invalid invoice number: {invoice_number}")
        data = {
            "version": VERSION,
            "cardType": card_type,
            "cardNo": card_number,
            "expTimeStamp": "2147483647",
            "action": "carrierInvDetail",
            "timeStamp": int(time() + self.ts_tolerance),
            "invNum": invoice_number,
            "invDate": invoice_date.strftime("%Y/%m/%d"),
            "uuid": self.uuid,
            "sellerName": seller_name,
            "amount": amount,
            "appID": self.app_id,
            "cardEncrypt": card_encrypt,
        }
        results = check_api_error(
            self.session.post(URL, data=data, timeout=self.timeout)
        )
        if not self.skip_validation:
            results = CarrierInvoicesDetailResponse.parse_obj(results)
        return results

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
        URL = build_api_url("donate")
        VERSION = 0.1
        if not validate_invoice_number(invoice_number):
            raise ValueError(f"Invalid invoice number: {invoice_number}")
        data = {
            "version": VERSION,
            "serial": f"{self.serial:0>10}",
            "cardType": card_type,
            "cardNo": card_number,
            "expTimeStamp": "2147483647",
            "action": "carrierInvDnt",
            "timeStamp": int(time() + self.ts_tolerance),
            "invDate": invoice_date.strftime("%Y/%m/%d"),
            "invNum": invoice_number,
            "npoBan": love_code,
            "uuid": self.uuid,
            "appID": self.app_id,
            "cardEncrypt": card_encrypt,
        }
        signature = sign(data, self.api_key)
        data["signature"] = signature
        self.serial += 1
        results = check_api_error(
            self.session.post(URL, data=data, timeout=self.timeout)
        )
        if not self.skip_validation:
            results = CarrierInvoiceDonateResponse.parse_obj(results)
        return results

    def get_aggregate_carrier(
        self,
        card_type: str,
        card_number: str,
        card_encrypt: str,
    ) -> Union[dict, AggregateCarrierResponse]:
        """手機條碼歸戶載具查詢 v1.0"""
        URL = build_api_url("carrier")
        VERSION = 1.0
        data = {
            "version": VERSION,
            "serial": f"{self.serial:0>10}",
            "action": "qryCarrierAgg",
            "cardType": card_type,
            "cardNo": card_number,
            "cardEncrypt": card_encrypt,
            "appID": self.app_id,
            "timeStamp": int(time() + self.ts_tolerance),
            "uuid": self.uuid,
        }
        signature = sign(data, self.api_key)
        data["signature"] = signature
        self.serial += 1
        results = check_api_error(
            self.session.post(URL, data=data, timeout=self.timeout)
        )
        if not self.skip_validation:
            results = AggregateCarrierResponse.parse_obj(results)
        return results
