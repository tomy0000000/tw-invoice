from datetime import date

import pytest

from tw_invoice import AppAPIClient
from tw_invoice.utils import build_api_url

TEST_API_KEY = "test_api_key"
TEST_APP_ID = "test_app_id"
TEST_CARD_ENCRYPT = "3f56c1f14f83b6eb"
TEST_CARD_NUMBER = "/AB12+-."
TEST_CARD_TYPE = "3J0002"
TEST_DATE = date(2020, 1, 1)
TEST_DATE_STR = "2020/01/01"
TEST_INVOICE_ENCRYPT = "ba1ddcbbb6f1183a"
TEST_INVOICE_NUMBER = "AB12345678"
TEST_INVOICE_TERM = "10902"
TEST_LOVE_CODE = "0"
TEST_RANDOM_NUMBER = 123
TEST_RANDOM_NUMBER_STR = "0123"
TEST_SELLER_ID = "12345678"
TEST_TIME = 1655654400
TEST_TS_TOLERANCE = 30
TEST_UUID = "test_uuid"


@pytest.fixture
def client():
    return AppAPIClient(TEST_APP_ID, TEST_API_KEY, TEST_UUID)


def test_plain_init():
    client = AppAPIClient(TEST_APP_ID, TEST_API_KEY)
    assert client.app_id == TEST_APP_ID
    assert client.api_key == TEST_API_KEY


# def test_init_with_env_vars():
#     client = AppAPIClient()
#     assert client.app_id == TEST_APP_ID
#     assert client.api_key == TEST_API_KEY


def test_init_with_optional_params():
    client = AppAPIClient(
        app_id=TEST_APP_ID,
        api_key=TEST_API_KEY,
        uuid=TEST_UUID,
        ts_tolerance=TEST_TS_TOLERANCE,
    )
    assert client.app_id == TEST_APP_ID
    assert client.api_key == TEST_API_KEY
    assert client.uuid == TEST_UUID
    assert client.ts_tolerance == TEST_TS_TOLERANCE


def test_init_with_invalid_ts_tolerance():
    with pytest.raises(ValueError):
        AppAPIClient(TEST_APP_ID, TEST_API_KEY, ts_tolerance=0)
    with pytest.raises(ValueError):
        AppAPIClient(TEST_APP_ID, TEST_API_KEY, ts_tolerance=181)


def test_get_lottery_numbers(client, mocker):
    with pytest.raises(ValueError):
        client.get_lottery_numbers("2022-04-23")

    # Mock the API response
    mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
    mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

    client.get_lottery_numbers("11006")
    mocked_session_post.assert_called_once_with(
        build_api_url("invapp"),
        data={
            "version": 0.2,
            "action": "QryWinningList",
            "invTerm": "11006",
            "UUID": TEST_UUID,
            "appID": TEST_APP_ID,
        },
    )
    mocked_check_api_error.assert_called_once()


def test_get_invoice_header(client, mocker):
    with pytest.raises(ValueError):
        client.get_invoice_header(
            barcode_type="invalid barcode",
            invoice_number=TEST_INVOICE_NUMBER,
            invoice_date=TEST_DATE,
        )

    with pytest.raises(ValueError):
        client.get_invoice_header(
            barcode_type="QRCode",
            invoice_number="invalid invoice number",
            invoice_date=TEST_DATE,
        )

    for barcode_type in ("QRCode", "Barcode"):
        # Mock the API response
        mocked_validate_invoice_number = mocker.patch(
            "tw_invoice.app_client.validate_invoice_number"
        )
        mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
        mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

        client.get_invoice_header(
            barcode_type=barcode_type,
            invoice_number=TEST_INVOICE_NUMBER,
            invoice_date=TEST_DATE,
        )
        mocked_validate_invoice_number.assert_called_once_with(TEST_INVOICE_NUMBER)
        mocked_session_post.assert_called_once_with(
            build_api_url("invapp"),
            data={
                "version": 0.5,
                "type": barcode_type,
                "invNum": TEST_INVOICE_NUMBER,
                "action": "qryInvHeader",
                "generation": "V2",
                "invDate": TEST_DATE_STR,
                "UUID": TEST_UUID,
                "appID": TEST_APP_ID,
            },
        )
        mocked_check_api_error.assert_called_once()


def test_get_invoice_detail(client, mocker):
    # Test invalid barcode type
    with pytest.raises(ValueError):
        client.get_invoice_detail(
            barcode_type="invalid barcode",
            invoice_number=TEST_INVOICE_NUMBER,
            invoice_date=TEST_DATE,
        )

    # Test QRCode without invoice encrypt
    with pytest.raises(ValueError):
        client.get_invoice_detail(
            barcode_type="QRCode",
            invoice_number=TEST_INVOICE_NUMBER,
            invoice_date=TEST_DATE,
        )

    # Test QRCode without seller id
    with pytest.raises(ValueError):
        client.get_invoice_detail(
            barcode_type="QRCode",
            invoice_number=TEST_INVOICE_NUMBER,
            invoice_date=TEST_DATE,
            invoice_encrypt=TEST_INVOICE_ENCRYPT,
        )

    # Test Barcode without invoice term
    with pytest.raises(ValueError):
        client.get_invoice_detail(
            barcode_type="Barcode",
            invoice_number=TEST_INVOICE_NUMBER,
            invoice_date=TEST_DATE,
        )

    # Test invalid invoice number
    with pytest.raises(ValueError):
        client.get_invoice_detail(
            barcode_type="QRCode",
            invoice_number="invalid invoice number",
            invoice_date=TEST_DATE,
            invoice_encrypt=TEST_INVOICE_ENCRYPT,
            seller_id=TEST_SELLER_ID,
        )

    # Test invalid invoice term
    with pytest.raises(ValueError):
        client.get_invoice_detail(
            barcode_type="Barcode",
            invoice_number=TEST_INVOICE_NUMBER,
            invoice_date=TEST_DATE,
            invoice_term="invalid invoice term",
        )

    # Mock the API response
    mocked_randrange = mocker.patch(
        "tw_invoice.app_client.randrange", return_value=TEST_RANDOM_NUMBER
    )
    mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
    mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

    client.get_invoice_detail(
        barcode_type="QRCode",
        invoice_number=TEST_INVOICE_NUMBER,
        invoice_date=TEST_DATE,
        invoice_encrypt=TEST_INVOICE_ENCRYPT,
        seller_id=TEST_SELLER_ID,
    )
    mocked_randrange.assert_called_once()
    mocked_session_post.assert_called_once_with(
        build_api_url("invapp"),
        data={
            "version": 0.5,
            "type": "QRCode",
            "invNum": TEST_INVOICE_NUMBER,
            "action": "qryInvDetail",
            "generation": "V2",
            "invTerm": None,
            "invDate": TEST_DATE_STR,
            "encrypt": TEST_INVOICE_ENCRYPT,
            "sellerID": TEST_SELLER_ID,
            "UUID": TEST_UUID,
            "randomNumber": TEST_RANDOM_NUMBER_STR,
            "appID": TEST_APP_ID,
        },
    )
    mocked_check_api_error.assert_called_once()

    # Mock the API response
    mocked_randrange = mocker.patch(
        "tw_invoice.app_client.randrange", return_value=TEST_RANDOM_NUMBER
    )
    mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
    mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

    client.get_invoice_detail(
        barcode_type="Barcode",
        invoice_number=TEST_INVOICE_NUMBER,
        invoice_date=TEST_DATE,
        invoice_term=TEST_INVOICE_TERM,
    )
    mocked_randrange.assert_called_once()
    mocked_session_post.assert_called_once_with(
        build_api_url("invapp"),
        data={
            "version": 0.5,
            "type": "Barcode",
            "invNum": TEST_INVOICE_NUMBER,
            "action": "qryInvDetail",
            "generation": "V2",
            "invTerm": TEST_INVOICE_TERM,
            "invDate": TEST_DATE_STR,
            "encrypt": None,
            "sellerID": None,
            "UUID": TEST_UUID,
            "randomNumber": TEST_RANDOM_NUMBER_STR,
            "appID": TEST_APP_ID,
        },
    )
    mocked_check_api_error.assert_called_once()


def test_get_love_code(client, mocker):
    # Mock the API response
    mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
    mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

    client.get_love_code("test-query")
    mocked_session_post.assert_called_once_with(
        build_api_url("lovecode"),
        data={
            "version": 0.2,
            "qKey": "test-query",
            "action": "qryLoveCode",
            "UUID": TEST_UUID,
            "appID": TEST_APP_ID,
        },
    )
    mocked_check_api_error.assert_called_once()


def test_get_carrier_invoices_header(client, mocker):
    # Mock the API response
    mocked_time = mocker.patch("tw_invoice.app_client.time", return_value=TEST_TIME)
    mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
    mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

    client.get_carrier_invoices_header(
        card_type=TEST_CARD_TYPE,
        card_number=TEST_CARD_NUMBER,
        start_date=TEST_DATE,
        end_date=TEST_DATE,
        card_encrypt=TEST_CARD_ENCRYPT,
    )
    mocked_time.assert_called_once()
    mocked_session_post.assert_called_once_with(
        build_api_url("invserv"),
        data={
            "version": 0.5,
            "cardType": TEST_CARD_TYPE,
            "cardNo": TEST_CARD_NUMBER,
            "expTimeStamp": "2147483647",
            "action": "carrierInvChk",
            "timeStamp": TEST_TIME + client.ts_tolerance,
            "startDate": TEST_DATE_STR,
            "endDate": TEST_DATE_STR,
            "onlyWinningInv": "N",
            "uuid": TEST_UUID,
            "appID": TEST_APP_ID,
            "cardEncrypt": TEST_CARD_ENCRYPT,
        },
    )
    mocked_check_api_error.assert_called_once()


def test_get_carrier_invoices_detail(client, mocker):
    # Test invalid invoice number
    with pytest.raises(ValueError):
        client.get_carrier_invoices_detail(
            card_type=TEST_CARD_TYPE,
            card_number=TEST_CARD_NUMBER,
            invoice_number="invalid invoice number",
            invoice_date=TEST_DATE,
            card_encrypt=TEST_CARD_ENCRYPT,
        )

    # Mock the API response
    mocked_time = mocker.patch("tw_invoice.app_client.time", return_value=TEST_TIME)
    mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
    mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

    client.get_carrier_invoices_detail(
        card_type=TEST_CARD_TYPE,
        card_number=TEST_CARD_NUMBER,
        invoice_number=TEST_INVOICE_NUMBER,
        invoice_date=TEST_DATE,
        card_encrypt=TEST_CARD_ENCRYPT,
    )
    mocked_time.assert_called_once()
    mocked_session_post.assert_called_once_with(
        build_api_url("invserv"),
        data={
            "version": 0.5,
            "cardType": TEST_CARD_TYPE,
            "cardNo": TEST_CARD_NUMBER,
            "expTimeStamp": "2147483647",
            "action": "carrierInvDetail",
            "timeStamp": TEST_TIME + client.ts_tolerance,
            "invNum": TEST_INVOICE_NUMBER,
            "invDate": TEST_DATE_STR,
            "uuid": TEST_UUID,
            "sellerName": None,
            "amount": None,
            "appID": TEST_APP_ID,
            "cardEncrypt": TEST_CARD_ENCRYPT,
        },
    )
    mocked_check_api_error.assert_called_once()


def test_carrier_donate_invoice(client, mocker):
    with pytest.raises(ValueError):
        client.carrier_donate_invoice(
            card_type=TEST_CARD_TYPE,
            card_number=TEST_CARD_NUMBER,
            invoice_date=TEST_DATE,
            invoice_number="invalid invoice number",
            love_code=TEST_LOVE_CODE,
            card_encrypt=TEST_CARD_ENCRYPT,
        )

    # Mock the API response
    mocked_time = mocker.patch("tw_invoice.app_client.time", return_value=TEST_TIME)
    mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
    mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

    client.carrier_donate_invoice(
        card_type=TEST_CARD_TYPE,
        card_number=TEST_CARD_NUMBER,
        invoice_date=TEST_DATE,
        invoice_number=TEST_INVOICE_NUMBER,
        love_code=TEST_LOVE_CODE,
        card_encrypt=TEST_CARD_ENCRYPT,
    )
    mocked_time.assert_called_once()
    mocked_session_post.assert_called_once_with(
        build_api_url("donate"),
        data={
            "version": 0.1,
            "serial": "0000000001",
            "cardType": TEST_CARD_TYPE,
            "cardNo": TEST_CARD_NUMBER,
            "expTimeStamp": "2147483647",
            "action": "carrierInvDnt",
            "timeStamp": TEST_TIME + client.ts_tolerance,
            "invDate": TEST_DATE_STR,
            "invNum": TEST_INVOICE_NUMBER,
            "npoBan": TEST_LOVE_CODE,
            "uuid": TEST_UUID,
            "appID": TEST_APP_ID,
            "cardEncrypt": TEST_CARD_ENCRYPT,
            "signature": "Ydmt4alIcCLYG/VBcI+QUdyfgO5Yp8bfX6TPy5xgsVs=",
        },
    )
    mocked_check_api_error.assert_called_once()
    assert client.serial == 2


def test_get_aggregate_carrier(client, mocker):
    # Mock the API response
    mocked_time = mocker.patch("tw_invoice.app_client.time", return_value=TEST_TIME)
    mocked_session_post = mocker.patch("tw_invoice.app_client.Session.post")
    mocked_check_api_error = mocker.patch("tw_invoice.app_client.check_api_error")

    client.get_aggregate_carrier(
        card_type=TEST_CARD_TYPE,
        card_number=TEST_CARD_NUMBER,
        card_encrypt=TEST_CARD_ENCRYPT,
    )
    mocked_time.assert_called_once()
    mocked_session_post.assert_called_once_with(
        build_api_url("carrier"),
        data={
            "version": 1.0,
            "serial": "0000000001",
            "action": "qryCarrierAgg",
            "cardType": TEST_CARD_TYPE,
            "cardNo": TEST_CARD_NUMBER,
            "cardEncrypt": TEST_CARD_ENCRYPT,
            "appID": TEST_APP_ID,
            "timeStamp": TEST_TIME + client.ts_tolerance,
            "uuid": TEST_UUID,
            "signature": "2pWN1GfP6S7oncE56OJetvpxGlE1tFYHeqgNwHmIuw4=",
        },
    )
    mocked_check_api_error.assert_called_once()
    assert client.serial == 2
