import pytest
from requests.exceptions import HTTPError
from requests.models import Response

from tw_invoice.exception import APIError
from tw_invoice.utils import (
    check_api_error,
    validate_invoice_number,
    validate_invoice_term,
    validate_phone_barcode,
)


@pytest.fixture
def client_error():
    response = Response()
    response.status_code = 404
    return response


@pytest.fixture
def server_error():
    response = Response()
    response.status_code = 500
    return response


@pytest.fixture
def api_error():
    response = Response()
    response.status_code = 200
    response.json = lambda: {"code": 998, "msg": "appID 不符合規定 (停權或尚未申請)"}
    return response


@pytest.fixture
def api_success():
    response = Response()
    response.status_code = 200
    response.json = lambda: {"code": "200", "msg": "OK"}
    return response


def test_check_api_error(client_error, server_error, api_error, api_success):
    # Test invalid type
    with pytest.raises(TypeError):
        check_api_error(None)

    # Test client error
    with pytest.raises(HTTPError):
        check_api_error(client_error)

    # Test server error
    with pytest.raises(HTTPError):
        check_api_error(server_error)

    # Test API error
    with pytest.raises(APIError):
        check_api_error(api_error)

    data = check_api_error(api_success)
    assert data["code"] == "200"


def test_validate_invoice_number():
    assert not validate_invoice_number(None)
    assert not validate_invoice_number("")
    assert not validate_invoice_number("5ab562e60d9ba2ee")
    assert not validate_invoice_number("AB")
    assert not validate_invoice_number("12345678")
    assert not validate_invoice_number("ab12345678")
    assert validate_invoice_number("AB12345678")


def test_validate_invoice_term():
    assert not validate_invoice_term(None)
    assert not validate_invoice_term("")
    assert not validate_invoice_term("5ab562e60d9ba2ee")
    assert not validate_invoice_term("202206")
    assert not validate_invoice_term("11105")
    assert validate_invoice_term("11106")


def test_validate_phone_barcode():
    assert not validate_phone_barcode(None)
    assert not validate_phone_barcode("")
    assert not validate_phone_barcode("5ab562e60d9ba2ee")
    assert not validate_phone_barcode("AB12+-.")
    assert validate_phone_barcode("/AB12+-.")
