import hashlib
import hmac
import re
from base64 import b64encode
from urllib.parse import urlencode, urljoin

from requests.models import Response

from .exception import APIError


def build_api_url(id: str) -> str:
    BASE_URL = "https://api.einvoice.nat.gov.tw"
    PATHS = {
        "invapp": "/PB2CAPIVAN/invapp/InvApp",
        "lovecode": "/PB2CAPIVAN/loveCodeapp/qryLoveCode",
        "invserv": "/PB2CAPIVAN/invServ/InvServ",
        "donate": "/PB2CAPIVAN/CarInv/Donate",
        "carrier": "/PB2CAPIVAN/Carrier/Aggregate",
    }
    return urljoin(BASE_URL, PATHS[id])


def sign(data: dict, key: str) -> str:
    """Generate signature"""
    data_pairs = [(name, value) for name, value in data.items() if value]
    data_pairs.sort(key=lambda x: x[0])
    query_string = urlencode(data_pairs, quote_via=lambda k, safe, encoding, errors: k)
    signature = b64encode(
        hmac.new(
            key=key.encode("utf-8"),
            msg=query_string.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).digest()
    ).decode("utf-8")
    return signature


def check_api_error(response: Response) -> dict:
    """Check API error"""
    if not isinstance(response, Response):
        raise TypeError("response must be a Response object")
    response.raise_for_status()
    data = response.json()
    if int(data["code"]) != 200:
        raise APIError(data["code"], data["msg"])
    return data


def validate_invoice_number(invoice_number: str) -> bool:
    """Validate einvoice number"""
    if not isinstance(invoice_number, str):
        return False
    return bool(re.match(r"^[A-Z]{2}\d{8}$", invoice_number))


def validate_invoice_term(invoice_term: str) -> bool:
    """Validate invoice term"""
    if not isinstance(invoice_term, str):
        return False
    return bool(re.match(r"^\d{3}(02|04|06|08|10|12)$", invoice_term))


def validate_phone_barcode(phone_barcode: str) -> bool:
    """Validate phone barcode"""
    if not isinstance(phone_barcode, str):
        return False
    return bool(re.match(r"^\/[A-Z0-9+.-]{7}$", phone_barcode))
