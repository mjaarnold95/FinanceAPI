from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.payroll import PayPeriodFrequency, PayStubLineType


class PayPeriodCreate(BaseModel):
    employer: str
    period_start: date
    period_end: date
    pay_date: date
    frequency: PayPeriodFrequency
    notes: Optional[str] = None


class PayPeriodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employer: str
    period_start: date
    period_end: date
    pay_date: date
    frequency: PayPeriodFrequency
    notes: Optional[str] = None
    created_at: datetime


class PayStubLineItemCreate(BaseModel):
    line_type: PayStubLineType
    description: str
    amount: Decimal
    ytd_amount: Decimal = Decimal("0")


class PayStubLineItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pay_stub_id: int
    line_type: PayStubLineType
    description: str
    amount: Decimal
    ytd_amount: Decimal


class PayStubCreate(BaseModel):
    gross_pay: Decimal
    net_pay: Decimal
    total_taxes: Decimal
    total_deductions: Decimal
    notes: Optional[str] = None
    line_items: list[PayStubLineItemCreate] = []


class PayStubRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    pay_period_id: int
    gross_pay: Decimal
    net_pay: Decimal
    total_taxes: Decimal
    total_deductions: Decimal
    notes: Optional[str] = None
    created_at: datetime
    line_items: list[PayStubLineItemRead] = []


class YTDSummary(BaseModel):
    year: int
    total_gross_pay: Decimal
    total_net_pay: Decimal
    total_taxes: Decimal
    total_deductions: Decimal
    by_category: dict[str, Decimal]
