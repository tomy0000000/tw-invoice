import pytest

from tw_invoice.exception import APIError

TEST_CODE = 1
TEST_MESSAGE = "Error Message"


def test_api_error():
    """Test APIError"""
    with pytest.raises(APIError):
        raise APIError(TEST_CODE, TEST_MESSAGE)

    error = APIError(TEST_CODE, TEST_MESSAGE)
    assert error.code == TEST_CODE
    assert error.message == TEST_MESSAGE
    assert str(TEST_CODE) in str(error)
    assert TEST_MESSAGE in str(error)
