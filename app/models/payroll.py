from enum import Enum
from datetime import date, datetime, timezone
from decimal import Decimal
from sqlalchemy import Numeric, Column
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional


class PayPeriodFrequency(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    SEMIMONTHLY = "semimonthly"
    MONTHLY = "monthly"


class PayStubLineType(str, Enum):
    EARNING = "earning"
    DEDUCTION = "deduction"
    TAX = "tax"
    EMPLOYER_CONTRIBUTION = "employer_contribution"


class PayPeriod(SQLModel, table=True):
    __tablename__ = "pay_periods"
    id: Optional[int] = Field(default=None, primary_key=True)
    employer: str
    period_start: date
    period_end: date
    pay_date: date
    frequency: PayPeriodFrequency
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pay_stubs: list["PayStub"] = Relationship(back_populates="pay_period")


class PayStub(SQLModel, table=True):
    __tablename__ = "pay_stubs"
    id: Optional[int] = Field(default=None, primary_key=True)
    pay_period_id: int = Field(foreign_key="pay_periods.id")
    gross_pay: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    net_pay: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    total_taxes: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    total_deductions: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pay_period: Optional[PayPeriod] = Relationship(back_populates="pay_stubs")
    line_items: list["PayStubLineItem"] = Relationship(back_populates="pay_stub")


class PayStubLineItem(SQLModel, table=True):
    __tablename__ = "pay_stub_line_items"
    id: Optional[int] = Field(default=None, primary_key=True)
    pay_stub_id: int = Field(foreign_key="pay_stubs.id")
    line_type: PayStubLineType
    description: str
    amount: Decimal = Field(sa_column=Column(Numeric(12, 2)))
    ytd_amount: Decimal = Field(default=Decimal("0"), sa_column=Column(Numeric(12, 2)))
    pay_stub: Optional[PayStub] = Relationship(back_populates="line_items")
