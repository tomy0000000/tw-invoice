from typing import List, Union

from pydantic import BaseModel

# LotteryNumberResponse


class LotteryNumberResponse(BaseModel):
    v: str
    code: str
    msg: str
    invoYm: str
    superPrizeNo: str
    spcPrizeNo: str
    spcPrizeNo2: Union[str, None] = None
    spcPrizeNo3: Union[str, None] = None
    firstPrizeNo1: str
    firstPrizeNo2: str
    firstPrizeNo3: str
    firstPrizeNo4: Union[str, None] = None
    firstPrizeNo5: Union[str, None] = None
    firstPrizeNo6: Union[str, None] = None
    firstPrizeNo7: Union[str, None] = None
    firstPrizeNo8: Union[str, None] = None
    firstPrizeNo9: Union[str, None] = None
    firstPrizeNo10: Union[str, None] = None
    sixthPrizeNo1: Union[str, None] = None
    sixthPrizeNo2: Union[str, None] = None
    sixthPrizeNo3: Union[str, None] = None
    superPrizeAmt: str
    spcPrizeAmt: str
    firstPrizeAmt: str
    secondPrizeAmt: str
    thirdPrizeAmt: str
    fourthPrizeAmt: str
    fifthPrizeAmt: str
    sixthPrizeAmt: str
    sixthPrizeNo4: Union[str, None] = None
    sixthPrizeNo5: Union[str, None] = None
    sixthPrizeNo6: Union[str, None] = None


# InvoiceHeaderResponse


class InvoiceHeaderResponse(BaseModel):
    v: str
    code: str
    msg: str
    invNum: str
    invDate: str
    sellerName: str
    invStatus: str
    invPeriod: str
    sellerBan: str
    sellerAddress: Union[str, None] = None
    invoiceTime: str
    buyerBan: Union[str, None] = None
    currency: Union[str, None] = None


# InvoiceDetailResponse


class InvoiceDetail(BaseModel):
    rowNum: str
    description: str
    quantity: str
    unitPrice: str
    amount: str


class InvoiceDetailResponse(BaseModel):
    # v: str  # For some reason this is not in the response
    code: str
    msg: str
    invNum: str
    invDate: str
    sellerName: str
    invStatus: str
    invPeriod: str
    sellerBan: str
    sellerAddress: str
    invoiceTime: str
    buyerBan: str
    currency: str
    amount: str
    details: Union[List[InvoiceDetail], None] = None


# LoveCodeResponse


class LoveCode(BaseModel):
    rowNum: int
    SocialWelfareBAN: str
    LoveCode: str
    SocialWelfareName: str
    SocialWelfareAbbrev: Union[str, None] = None


class LoveCodeResponse(BaseModel):
    v: str
    code: str
    msg: str
    details: List[LoveCode]


# CarrierInvoicesHeaderResponse


class InvoiceDate(BaseModel):
    year: int
    month: int
    date: int
    day: int
    hours: int
    minutes: int
    seconds: int
    time: int
    timezoneOffset: int


class Invoice(BaseModel):
    rowNum: str
    invNum: str
    cardType: str
    cardNo: str
    sellerName: str
    invStatus: str
    invDonatable: bool
    amount: str
    invPeriod: str
    donateMark: bool  # served in 0 or 1, will be cast implicitly to bool
    sellerBan: str
    sellerAddress: Union[str, None] = None
    invoiceTime: str
    buyerBan: Union[str, None] = None
    currency: Union[str, None] = None
    invDate: InvoiceDate


class CarrierInvoicesHeaderResponse(BaseModel):
    v: str
    code: int
    msg: str
    onlyWinningInv: str
    details: List[Invoice]


# CarrierInvoicesDetailResponse


class CarrierInvoicesDetailResponse(BaseModel):
    v: str
    code: int
    msg: str
    invNum: str
    invDate: str
    sellerName: str
    amount: str
    invStatus: str
    invPeriod: str
    details: List[InvoiceDetail]
    sellerBan: str
    sellerAddress: str
    invoiceTime: str
    currency: str


# CarrierInvoiceDonateResponse


class CarrierInvoiceDonateResponse(BaseModel):
    v: str
    code: int
    msg: str
    hashSerial: str
    invNum: str
    invDate: str
    NPOBan: str
    invStatus: str
    invDntTimeStamp: str


# AggregateCarrierResponse


class Carrier(BaseModel):
    carrierType: str
    carrierId2: str
    carrierName: str


class AggregateCarrierResponse(BaseModel):
    v: str
    code: int
    hashSerial: str
    msg: str
    cardType: str
    cardNo: str
    carriers: List[Carrier]
